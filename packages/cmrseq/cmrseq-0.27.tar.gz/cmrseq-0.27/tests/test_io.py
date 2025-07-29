import unittest

from copy import deepcopy
import os
import sys

from pint import Quantity
import matplotlib.pyplot as plt
import numpy as np
import cmrseq
from cmrseq.io import PulseSeqFile
import pypulseq as pp

resource_dir = f"{os.path.dirname(__file__)}/resources"
sys.path.append(resource_dir)
test_out_dir = f"{os.path.dirname(__file__)}/output/io_module"
os.makedirs(test_out_dir, exist_ok=True)

class TestIOJSON(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.01, "ms"))

        fov = Quantity([202, 22], "mm")
        matrix_size = np.array((101, 11))
        res = fov / matrix_size
        adc_duration = Quantity(2., "ms")
        pulse_duration = Quantity(1.5, "ms")
        slice_thickness = Quantity(2, "cm")
        flip_angle = Quantity(12, "degree").to("rad")

        print("Resolution:", res)

        n_dummy = 0
        self.sequence_list = cmrseq.seqdefs.sequences.flash(self.system_specs,
                                                            slice_thickness=slice_thickness,
                                                            flip_angle=flip_angle,
                                                            pulse_duration=pulse_duration,
                                                            time_bandwidth_product=6,
                                                            matrix_size=matrix_size,
                                                            inplane_resolution=res,
                                                            adc_duration=adc_duration,
                                                            echo_time=Quantity(3., "ms"),
                                                            repetition_time=Quantity(10., "ms"),
                                                            dummy_shots=n_dummy)

    def test_save_and_load(self):

        cmrseq.io._json.sequence_to_json(self.sequence_list[0], f"{test_out_dir}/test_block")
        seq = cmrseq.io._json.sequence_from_json(f"{test_out_dir}/test_block.json")
        cmrseq.plotting.plot_sequence(seq)


class TestIOPulseq(unittest.TestCase):
    @staticmethod
    def _compare_moments(seq: cmrseq.Sequence, ppseq: pp.Sequence, atol=1e-4) -> bool:
        """

        :param seq:
        :param ppseq:
        :param atol: in Hz/m*s
        :return:
        """
        gw = ppseq.waveforms()
        ppmoments = []
        for (t, g) in gw:
            ppmoments.append(np.trapz(g, t))
        ppmoments = Quantity(ppmoments, "Hz/m*s").m
        cmr_moment = seq.calculate_moment()
        cmr_moment = (cmr_moment * seq._system_specs.gamma).m_as("Hz/m*s")
        return np.allclose(cmr_moment, ppmoments, atol=atol)

    @staticmethod
    def _compare_kspace(seq: cmrseq.Sequence, ppseq: pp.Sequence, dwell_time: Quantity) -> bool:
        """Timing is checked by comparing the k-space samples. 
        :param seq:
        :param ppseq:
        :param dwell_time:
        :return:
        """
        cmr_k_traj, cmr_kvecs, cmr_t_adc = seq.calculate_kspace()
        pp_kvecs, pp_k_traj, pp_t_exc, pp_t_ref, pp_t_adc = ppseq.calculate_kspace()
        ref_kdiff = (seq._system_specs.max_grad * dwell_time / 2 * seq._system_specs.gamma)
        max_kdiff = np.max(pp_kvecs[:, :cmr_kvecs.shape[1]] - cmr_kvecs, axis=1)

        tadc_diff = pp_t_adc[:cmr_t_adc.shape[0]]*1000 - cmr_t_adc
        times_close = np.allclose(tadc_diff, 0, rtol=1e-4)

        k_space_close = np.allclose(max_kdiff, 0, atol=1e-4)
        return all([times_close, k_space_close])

    @staticmethod
    def _compare_report_values(seq: cmrseq.Sequence, ppseq: pp.Sequence):
        cmr_report = cmrseq.utils.report(seq, format="dict")
        ppreport = ppseq.test_report()
        ppreport = {k: v for (k, v) in [l.split(":") for l in ppreport.split("\n") if len(l.split(":")) == 2]}

        tr_equal = np.allclose(Quantity(float(ppreport["TR"].replace('s', '')), "s").m_as("ms"),
                               cmr_report["pulse_gap"].m_as("ms"))
        flip_equal = np.allclose(Quantity(float(ppreport["Flip angle"].replace('deg', '')), "degree").m_as("degree"),
                                 cmr_report["flip_angles"].m_as("degree"))

        return tr_equal, flip_equal

    def test_write_cmrseq_bssfp(self):
        seq_list = cmrseq.seqdefs.sequences.balanced_ssfp(system_specs=cmrseq.SystemSpec(),
                                                          matrix_size=np.array([100, 50]),
                                                          inplane_resolution=Quantity([5, 5], "mm"),
                                                          slice_thickness=Quantity(10, "mm"),
                                                          adc_duration=None,
                                                          flip_angle=Quantity(25, "degree"),
                                                          pulse_duration=None,
                                                          repetition_time=Quantity(4.1,'ms'),
                                                          dummy_shots=0)

        seq = deepcopy(seq_list[0])
        seq.extend(seq_list[1:], copy=False)
        pf0 = PulseSeqFile(sequence=seq)
        pf0.write(f"{test_out_dir}/trufi_out.seq")

    def test_read_pulseseq_gre(self):
        """This test exports an example sequence using pypulseq and subsequently reads the
        file using CMRseq. Flip angles and TRs are compared to ensure correct conversion
        """
        # The reference values are hardcoded in the main function of the given example, hence this
        # test will definitely fail if the reference is changed
        from pypulseq_write_gre import main
        main(plot=False, write_seq=True, seq_filename=f"{resource_dir}/pulseq_gre.seq")

        # The system specification listed below must correspond to the definitions in the
        # pypulseq example sequence. Hence, this test might fail if the reference 'main' function
        # is changed...
        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(28, "mT/m"),
            max_slew=Quantity(150, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(100, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )

        pfile = PulseSeqFile(file_path=os.path.abspath(f"{resource_dir}/pulseq_gre.seq"))
        sequence_list = pfile.to_cmrseq(system_specs)
        seq1 = deepcopy(sequence_list[0])
        seq1.extend(sequence_list[1:], copy=False)

        ppseq = pp.Sequence()
        ppseq.read(f"{resource_dir}/pulseq_gre.seq")

        self.assertTrue(all(self._compare_report_values(seq1, ppseq)))
        self.assertTrue(self._compare_kspace(seq1, ppseq, seq1["adc_0"]._dwell))

    def test_cmrseq_epi(self):
        """Constructs a single shot EPI readout in CMRseq, exports it to pulseq and loads it with
        pypulseq. Checks if pypulseq reports valid timing, if difference in k-space position is
        zero"""
        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(32, "mT/m"),
            max_slew=Quantity(150, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(100, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )
        seq = cmrseq.seqdefs.readout.single_shot_epi(system_specs,
                                                     Quantity([10, 10], "cm"),
                                                     matrix_size=np.array([100, 100]),
                                                     slope_sampling=True)
        fig = cmrseq.plotting.plot_sequence(seq, axes="single")
        fig.savefig(f"{test_out_dir}/cmrseq_epi.png")
        pfile = PulseSeqFile(sequence=seq)
        pfile.write(f"{test_out_dir}/cmrseq_epi_def.seq")

        seqpp = pp.Sequence()
        seqpp.read(f"{test_out_dir}/cmrseq_epi_def.seq")
        self.assertTrue(seqpp.check_timing()[0])
        print(seqpp.test_report())

        with self.subTest("Same total moments per channel"):
            self._compare_moments(seq, seqpp, atol=1e-4)

        with self.subTest("Compare kspace locations"):
            self._compare_kspace(seq, seqpp, seq["adc_0"]._dwell)

    def test_cmrseq_pcgre(self):
        """Instantiates the cmrseq phase-contrast definition and exports it to Pulseq, then loads
        it with pypulseq and checks if definition is valid. Furthermore, checks if all trapezoidals
        are exported correctly and the number of blocks are correct.
        """
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                         max_slew=Quantity(120., "mT/m/ms"),
                                         grad_raster_time=Quantity(10, "us"),
                                         rf_raster_time=Quantity(1, "us"),
                                         adc_raster_time=Quantity(100, "ns"))
        fov = Quantity([200, 200], "mm")
        matrix_size = np.array((100, 100))
        res = fov / matrix_size
        pulse_duration = Quantity(1.5, "ms")
        adc_duration = Quantity(2, "ms")
        flip_angle = Quantity(np.pi / 6, "rad")
        slice_thickness = Quantity(3, "mm")
        venc_max = Quantity(60, "cm/s")
        venc_direction = np.array([0., 1., 0.])  # in mps

        sequence_list = cmrseq.contrib.pc_gre(system_specs,
                                              matrix_size=matrix_size,
                                              inplane_resolution=res,
                                              slice_thickness=slice_thickness,
                                              adc_duration=adc_duration,
                                              flip_angle=flip_angle,
                                              pulse_duration=pulse_duration,
                                              repetition_time=Quantity(9., "ms"),
                                              echo_time=Quantity(1., "ms"),
                                              venc=venc_max.to("m/s"),
                                              venc_direction=venc_direction,
                                              venc_duration=Quantity(0., "ms"))
        sequence = sequence_list[0].copy()
        sequence.extend(sequence_list[1:])
        with self.subTest("Write to file"):
            pf2 = PulseSeqFile(sequence=sequence)
            pf2.write(f"{test_out_dir}/cmrseq_pc_gre.seq")
            cmr_pfil2 = PulseSeqFile(file_path=f"{test_out_dir}/cmrseq_pc_gre.seq")
            self.assertTrue(len(cmr_pfil2.grads_table) == 0)
            self.assertTrue(len(cmr_pfil2.adc_table) == 1)

        with self.subTest("Compare with pulseq"):
            ppseq = pp.Sequence()
            ppseq.read(f"{test_out_dir}/cmrseq_pc_gre.seq")
            self.assertTrue(ppseq.check_timing()[0])
            ppseq.test_report()

        print(self._compare_report_values(sequence, ppseq))

    def test_cmrseq_flash(self):
        """Instantiates the cmrseq spoiled GRE definition and exports it to Pulseq, then loads
        it with pypulseq and checks if definition is valid. Furthermore, checks if all trapezoidals
        are exported correctly and the number of blocks are correct. """
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                         max_slew=Quantity(120., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(1, "us"),
                                         adc_raster_time=Quantity(100, "ns"),
                                         )
        fov = Quantity([200, 200], "mm")
        matrix_size = np.array((100, 100))
        res = fov / matrix_size
        pulse_duration = Quantity(1.5, "ms")
        adc_duration = Quantity(2000, "us")
        flip_angle = Quantity(np.pi / 6, "rad")
        slice_normal = np.array([0., 0., 1])
        slice_normal = slice_normal / np.linalg.norm(slice_normal)
        slice_position = Quantity([0, 0, 0], "cm")
        slice_position_offset = Quantity(np.dot(slice_normal, slice_position.m_as("m")), "m")
        slice_thickness = Quantity(3, "mm")
        time_bandwidth_product = 4
        sequence_list = cmrseq.seqdefs.sequences.flash(system_specs,
                                                       slice_thickness=slice_thickness,
                                                       flip_angle=flip_angle,
                                                       pulse_duration=pulse_duration,
                                                       time_bandwidth_product=time_bandwidth_product,
                                                       matrix_size=matrix_size,
                                                       inplane_resolution=res,
                                                       adc_duration=adc_duration,
                                                       echo_time=None,
                                                       repetition_time=None,
                                                       slice_position_offset=slice_position_offset,
                                                       rf_spoil=False)

        plt.close("all")
        f, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={'width_ratios': [5, 2]})
        cmrseq.plotting.plot_sequence(sequence_list[0], axes=a1, adc_yoffset=15.7)
        sequence = deepcopy(sequence_list[0])
        print(sequence["adc_0"].duration)
        sequence.extend(sequence_list[1:], copy=False)

        with self.subTest("Write to file"):
            pf2 = PulseSeqFile(sequence=sequence)
            pf2.write(f"{test_out_dir}/cmr_pcmri.seq")
            cmr_pfil2 = PulseSeqFile(file_path=f"{test_out_dir}/cmr_pcmri.seq")
            self.assertTrue(len(cmr_pfil2.grads_table) == 0)
            self.assertTrue(len(cmr_pfil2.adc_table) == 1)

        with self.subTest("Compare with pulseq"):
            ppseq = pp.Sequence()
            ppseq.read(f"{test_out_dir}/cmr_pcmri.seq")
            self.assertTrue(ppseq.check_timing()[0],
                            msg=f"Assumed timing to be correct but received\n{ppseq.check_timing()[1]}")
            ppseq.test_report()

    def test_pulseq_gre_to_cmrseq(self):
        """Writes a GRE with pypulseq to file loads it and converts it back to pulseq.

        Checks if the sequence parameters and block-durations are consistent with the input
        If test_read_pulseseq_gre fails, this could also be the root cause of this test failing...
        """
        # The reference values are hardcoded in the main function of the given example, hence this
        # test will definitely fail if the reference is changed
        from pypulseq_write_gre import main
        main(plot=False, write_seq=True, seq_filename=f"{resource_dir}/pulseq_gre.seq")
        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(28, "mT/m"),
            max_slew=Quantity(150, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(100, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )

        with self.subTest("Load from file"):
            pfile = PulseSeqFile(file_path=os.path.abspath(f"{resource_dir}/pulseq_gre.seq"))
            sequence_list = pfile.to_cmrseq(system_specs)
            seq = sequence_list[0].copy()
            seq.extend(sequence_list[1:], copy=False)

        with self.subTest("CMrseq -> Pulseq write and check with pypulseq"):
            pfile2 = PulseSeqFile(sequence=seq)
            pfile2.write(f"{resource_dir}/pulseq_gre_inout.seq")
            seqpp = pp.Sequence()
            seqpp.read(f"{resource_dir}/pulseq_gre_inout.seq")
            self.assertTrue(seqpp.check_timing()[0])

        seqpp = pp.Sequence()
        seqpp.read(f"{resource_dir}/pulseq_gre.seq")
        self._compare_kspace(seq, seqpp, seq["adc_0"]._dwell)
        self._compare_report_values(seq, seqpp)

    def test_take_previous_blockborder(self):
        """Construct a sequence of trapezoids with one RF, that must result in non-spit-gradients,
        while testing the case of identical start times of different channels.
        This case requires to correctly push back the first GY gradient due to the collision in the
        GZ channel
        """
        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(40, "mT/m"),
            max_slew=Quantity(120, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(100, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )
        sequence = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(system_specs,
                                                                        Quantity(10, "mm"),
                                                                        Quantity(30, "degree"))

        trap1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs, np.array([2., 1., 0.]),
                                                                  sequence[2].duration,
                                                                  sequence[2].amplitude * 0.9,
                                                                  delay=sequence[0].tmax)
        sequence.add_block(trap1)
        trap2 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([0., 1., 0.]),
                                                     Quantity(10, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"), delay=sequence.end_time)
        trap3 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([1., 0., 0.]),
                                                     Quantity(12, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"), delay=sequence.end_time)
        sequence.add_block(trap2)
        sequence.add_block(trap3)
        f = cmrseq.plotting.plot_sequence(sequence, axes="single")
        f.savefig(f"{test_out_dir}/edgecase_0.png")

        with self.subTest("Write to pulseq file"):
            cmr_to_pulseq_file = PulseSeqFile(sequence=sequence)
            cmr_to_pulseq_file.write(f"{test_out_dir}/edgecase_0.seq")
            cmr_pfil2 = PulseSeqFile(file_path=f"{test_out_dir}/edgecase_0.seq")
            self.assertTrue(len(cmr_pfil2.grads_table)==0)

        with self.subTest("Load and rewrite with pulseq"):
            ppseq = pp.Sequence()
            ppseq.read(f"{test_out_dir}/edgecase_0.seq")
            ppseq.check_timing()

    def test_cmrseq_to_pulseq_splitgradient1(self):
        """Constructs a sequence of 3 trapezoidals, which require the split of the Gy trapezoidal
        to write to pulseq. Subsequently, the sequence is exported to pulseq, loaded with pypulseq
        and the gradient moments are compared by value.
        """

        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(40, "mT/m"),
            max_slew=Quantity(120, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(100, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )
        trap1 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([1, 0., 0.]),
                                                     Quantity(10, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"))
        trap2 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([0., 1., 0.]),
                                                     Quantity(10, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"),
                                                     delay=Quantity(0.35, "ms"))

        seq = cmrseq.Sequence([trap1, trap2], system_specs, copy=True)
        trap1.shift(Quantity(-0.2, "ms"))
        seq.append(trap1)
        f = cmrseq.plotting.plot_sequence(seq, axes="single")
        f.savefig(f"{test_out_dir}/edgecase_1.png")

        with self.subTest("Write to pulseq file"):
            cmr_to_pulseq_file = PulseSeqFile(sequence=seq)
            cmr_to_pulseq_file.write(f"{test_out_dir}/edgecase_1.seq")

        with self.subTest("Load and rewrite with pulseq"):
            ppseq = pp.Sequence()
            ppseq.read(f"{test_out_dir}/edgecase_1.seq")
            ppseq.write(f"{test_out_dir}/edgecase_11.seq")
            self.assertTrue(ppseq.check_timing()[0])

        with self.subTest("Compare gradient moments"):
            self.assertTrue(self._compare_moments(seq, ppseq))

    def test_cmrseq_to_pulseq_splitgradient2(self):
        """Constructs a sequence of 4 trapezoidals, which require the split of the Gy trapezoidal
        to write to pulseq. Subsequently, the sequence is exported to pulseq, loaded with pypulseq
        and the gradient moments are compared by value.
        """

        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(40, "mT/m"),
            max_slew=Quantity(120, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(100, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )
        trap0 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([0., 1., 0.]),
                                                     Quantity(10, "mT/m"), Quantity(0., "ms"),
                                                     Quantity(0.1, "ms"))
        trap1 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([1, 0., 0.]),
                                                     Quantity(10, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"))
        trap2 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([0., 1., 0.]),
                                                     Quantity(10, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"),
                                                     delay=Quantity(0.35, "ms"))

        seq = cmrseq.Sequence([trap0, trap1, trap2], system_specs, copy=True)
        trap1.shift(Quantity(-0.2, "ms"))
        seq.append(trap1)
        f = cmrseq.plotting.plot_sequence(seq, axes="single")
        f.savefig(f"{test_out_dir}/edgecase_2.png")

        with self.subTest("Write to pulseq file"):
            cmr_to_pulseq_file = PulseSeqFile(sequence=seq)
            cmr_to_pulseq_file.write(f"{test_out_dir}/edgecase_2.seq")

        with self.subTest("Load and rewrite with pulseq"):
            ppseq_file = pp.Sequence()
            ppseq_file.read(f"{test_out_dir}/edgecase_2.seq")
            ppseq_file.plot(save=True)
            ppseq_file.write(f"{test_out_dir}/edgecase_21.seq")

        with self.subTest("Compare gradient moments"):
            cmrseq_moment = seq.calculate_moment()
            gw = ppseq_file.waveforms()
            ppmoments = []
            for (t, g) in gw:
                ppmoments.append(np.trapz(g, t))
            val_pp = Quantity(ppmoments, "Hz/m*s").m
            val_cmr = (cmrseq_moment * system_specs.gamma).m_as("Hz/m*s")
            self.assertTrue(np.allclose(val_pp, val_cmr),
                            msg=f"Gradient moments are different"
                                f"\n\tpulseq {val_pp}\n\tcmrseq {val_cmr}")

    def test_cmrseq_to_pulseq_splitgradient3(self):
        """Constructs a sequence of 2 trapezoids and two sinc pulses,
        which require the split of the second trapezoidal to write to pulseq.
        """

        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(40, "mT/m"),
            max_slew=Quantity(120, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(100, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )

        trap1 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([1, 0., 0.]),
                                                     Quantity(10, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"))
        trap2 = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([0., 0., 1.]),
                                                     Quantity(10, "mT/m"), Quantity(0.6, "ms"),
                                                     Quantity(0.1, "ms"),
                                                     delay=Quantity(1., "ms"))
        sinc1 = cmrseq.bausteine.SincRFPulse(system_specs, duration=trap1.flat_duration,
                                             flip_angle=Quantity(45, "degree"),
                                             time_bandwidth_product=4,
                                             delay=trap1.rise_time)
        sinc2 = cmrseq.bausteine.SincRFPulse(system_specs, duration=trap1.flat_duration,
                                             flip_angle=Quantity(45, "degree"),
                                             time_bandwidth_product=4,
                                             delay=trap2.rise_time+trap2.tmin)

        seq = cmrseq.Sequence([trap1, sinc1, trap2, sinc2], system_specs, copy=True)
        f = cmrseq.plotting.plot_sequence(seq, axes="single")
        f.savefig(f"{test_out_dir}/edgecase_3.png")

        with self.subTest("Write to pulseq file"):
            cmr_to_pulseq_file = PulseSeqFile(sequence=seq)
            cmr_to_pulseq_file.write(f"{test_out_dir}/edgecase_3.seq")

        with self.subTest("Load and rewrite with pulseq"):
            ppseq_file = pp.Sequence()
            ppseq_file.read(f"{test_out_dir}/edgecase_3.seq")
            ppseq_file.write(f"{test_out_dir}/edgecase_31.seq")

        with self.subTest("Compare gradient moments"):
            cmrseq_moment = seq.calculate_moment()
            gw = ppseq_file.waveforms()
            ppmoments = []
            for (t, g) in gw:
                ppmoments.append(np.trapz(g, t))
            val_pp = Quantity(ppmoments, "Hz/m*s").m
            val_cmr = (cmrseq_moment * system_specs.gamma).m_as("Hz/m*s")
            self.assertTrue(np.allclose(val_pp, val_cmr),
                            msg=f"Gradient moments are different"
                                f"\n\tpulseq {val_pp}\n\tcmrseq {val_cmr}")
            
    def test_cmrseq_to_pulseq_gradientmerging(self):
        """Constructs a sequence of 2 trapezoids and one RF/ADC,
        which requires to combined the trapezoids to prevent splitting of the RF/ADC.
        """

        system_specs = cmrseq.SystemSpec(
            max_grad=Quantity(40, "mT/m"),
            max_slew=Quantity(120, "mT/m/ms"),
            rf_ringdown_time=Quantity(20, "us"),
            rf_dead_time=Quantity(10, "us"),
            adc_dead_time=Quantity(10, "us"),
            grad_raster_time=Quantity(10, "us"),
            rf_raster_time=Quantity(1, "us"),
            adc_raster_time=Quantity(100, "ns")
        )

        trap1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs, np.array([1, 0., 0.]),
                                                                  duration=Quantity(1, "ms"),
                                                                  amplitude=Quantity(10, "mT/m"))
        trap2 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs, np.array([1, 0., 0.]),
                                                                  duration=Quantity(1, "ms"),
                                                                  amplitude=Quantity(10, "mT/m"),
                                                                  delay=Quantity(1.2, "ms"))
        sinc = cmrseq.bausteine.SincRFPulse(system_specs, duration=Quantity(2, "ms"),
                                             flip_angle=Quantity(45, "degree"), delay = Quantity(20,'us'))
        
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(system_specs=system_specs,
                                                                 num_samples=121,
                                                                 duration=Quantity(2, "ms"), delay = Quantity(20,'us'))


        seq = cmrseq.Sequence([trap1, sinc, trap2], system_specs, copy=True)
        seq2 = cmrseq.Sequence([trap1, adc, trap2], system_specs, copy=True)
        f = cmrseq.plotting.plot_sequence(seq, axes="single")
        f.savefig(f"{test_out_dir}/edgecase_4_rf.png")

        f = cmrseq.plotting.plot_sequence(seq2, axes="single")
        f.savefig(f"{test_out_dir}/edgecase_4_adc.png")

        with self.subTest("Write RF seq to pulseq file"):
            cmr_to_pulseq_file = PulseSeqFile(sequence=seq)
            cmr_to_pulseq_file.write(f"{test_out_dir}/edgecase_4_rf.seq")

        with self.subTest("Write ADC seq to pulseq file"):
            cmr_to_pulseq_file = PulseSeqFile(sequence=seq2)
            cmr_to_pulseq_file.write(f"{test_out_dir}/edgecase_4_adc.seq")

        with self.subTest("Load rf seq and rewrite with pulseq"):
            ppseq_file = pp.Sequence()
            ppseq_file.read(f"{test_out_dir}/edgecase_4_rf.seq")
            ok, error = ppseq_file.check_timing()
            self.assertTrue(ok, msg=f"Loaded rf seq pulseq file timing not valid")

        with self.subTest("Load adc seq and rewrite with pulseq"):
            ppseq_file = pp.Sequence()
            ppseq_file.read(f"{test_out_dir}/edgecase_4_adc.seq")
            ok, error = ppseq_file.check_timing()
            self.assertTrue(ok, msg=f"Loaded adc seq pulseq file timing not valid")

    # This test has been disabled, as there is a logic conflict when the ADC raster is <1us
    # This seems to be a fundemental issue with the pulseq format, unless all ADC events must also start on a us raster
    # Then the only solution is rounding (or just define the sequence on a us raster?) 

    # def test_invalid_adc_delay(self):
    #     """Creates a trapezoid with an ADC that requires a delay not expressible as integer
    #      microsecond value, and checks if ValueError is raised during conversion.
    #     """
    #     system_specs = cmrseq.SystemSpec(
    #         max_grad=Quantity(40, "mT/m"),
    #         max_slew=Quantity(120, "mT/m/ms"),
    #         rf_ringdown_time=Quantity(20, "us"),
    #         rf_dead_time=Quantity(100, "us"),
    #         adc_dead_time=Quantity(10, "us"),
    #         grad_raster_time=Quantity(10, "us"),
    #         rf_raster_time=Quantity(1, "us"),
    #         adc_raster_time=Quantity(100, "ns")
    #     )
    #     flat_time = Quantity(1, "ms")

    #     grad = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(system_specs,
    #                                                               orientation=np.array([1., 0., 0.]),
    #                                                               flat_duration=flat_time,
    #                                                               amplitude=Quantity(10, "mT/m"))
    #     adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(system_specs, 121,
    #                                                             duration=flat_time,
    #                                                             delay=grad.rise_time)
    #     start_padding = adc.tmin - grad.rise_time
    #     self.assertTrue(np.isclose(start_padding.to("us"), Quantity(3.9, "us"), atol=1e-6))

    #     # As 3.9us is not a integer value of us, the conversion of cmrseq to Pulseq should raise
    #     # an ValueError to prevent silent rounding
    #     sequence = cmrseq.Sequence([grad, adc], system_specs)
    #     self.assertRaises(ValueError, lambda: PulseSeqFile(sequence=sequence))
