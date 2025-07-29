import unittest
import os
from copy import deepcopy

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq

test_plot_output = f"{os.path.dirname(__file__)}/output/seqdefs_sequences/"
os.makedirs(test_plot_output, exist_ok=True)


class TestFlashCartesian(unittest.TestCase):
    """ Tests for GradientEcho cartesian readout definitions"""

    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

    def test_instantiate(self):
        echo_time = None
        repetition_time = Quantity(6., "ms")
        matrix_size = np.array([11, 11])
        inplane_resolution = Quantity([1, 1], "mm")
        slice_thickness = Quantity(10, "mm")
        adc_duration = Quantity(2.5, "ms")
        pulse_duration = Quantity(1.5, "ms")
        flip_angle = Quantity(np.pi / 4, "rad")

        seq_list = cmrseq.seqdefs.sequences.flash(system_specs=self.system_specs,
                                                  matrix_size=matrix_size,
                                                  inplane_resolution=inplane_resolution,
                                                  slice_thickness=slice_thickness,
                                                  adc_duration=adc_duration,
                                                  flip_angle=flip_angle,
                                                  pulse_duration=pulse_duration,
                                                  repetition_time=repetition_time,
                                                  echo_time=echo_time,
                                                  slice_position_offset=Quantity(0., "m"),
                                                  time_bandwidth_product=4.,
                                                  fuse_slice_rewind_and_prephaser=True,
                                                  dummy_shots=0)

        f, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios": (2, 1)})
        cmrseq.plotting.plot_sequence(seq_list[0], a1, format_axes=True)
        for seq in seq_list[1:]:
            cmrseq.plotting.plot_sequence(seq, axes=[f.axes[2], a1, a1, a1], format_axes=False)
            cmrseq.plotting.plot_kspace_2d(seq, k_axes=(0, 1), ax=a2)

        f.suptitle("Spoiled GRE")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/flash_cartesian.svg")
        plt.close(f)

    def test_grid_sequence(self):
        # Define MR-system specifications
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"),
                                         adc_raster_time=Quantity(0.001, "ms"))

        fov = Quantity([101, 101], "mm")
        matrix_size = (21, 21)
        res = fov / matrix_size
        adc_duration = Quantity(2., "ms")
        pulse_duration = Quantity(1.5, "ms")
        slice_thickness = Quantity(2, "cm")
        flip_angle = Quantity(12, "degree").to("rad")

        print("Resolution:", res)

        n_dummy = 5
        sequence_list = cmrseq.seqdefs.sequences.flash(system_specs,
                                                       slice_thickness=slice_thickness,
                                                       flip_angle=flip_angle,
                                                       pulse_duration=pulse_duration,
                                                       time_bandwidth_product=6,
                                                       matrix_size=matrix_size,
                                                       inplane_resolution=res,
                                                       adc_duration=adc_duration,
                                                       echo_time=None,
                                                       repetition_time=Quantity(10., "ms"),
                                                       fuse_slice_rewind_and_prephaser=True,
                                                       dummy_shots=n_dummy)

        crusher_area = Quantity(np.pi * 6, "rad") / system_specs.gamma_rad / res[0]
        crusher = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                     orientation=np.array(
                                                                         [1., 0., 0.]),
                                                                     duration=Quantity(2.5, "ms"),
                                                                     area=crusher_area.to(
                                                                         "mT/m*ms"),
                                                                     delay=Quantity(5.5, "ms"))
        sequence_list = [seq + cmrseq.Sequence([deepcopy(crusher)], system_specs) for seq in
                         sequence_list]

        k_grad, k_adc, t_adc = sequence_list[n_dummy + 1].calculate_kspace()
        t_center = Quantity(t_adc[matrix_size[0] // 2], "ms")

        combined_sequence_dummyshots = deepcopy(sequence_list[0])
        combined_sequence_dummyshots.extend(sequence_list[1:n_dummy])

        combined_sequence = deepcopy(sequence_list[n_dummy])
        for idx, seq in enumerate(sequence_list[n_dummy:]):
            seq.get_block("adc_0").phase_offset = Quantity(np.pi /2 * (-1)**idx, "rad")

        combined_sequence.extend(sequence_list[n_dummy + 1:], copy=False)
        _ = [np.stack(v) for v in cmrseq.utils.grid_sequence_list([combined_sequence_dummyshots, ])]
        t_comb, rf_comb, grad_comb, adc_on_comb = [np.stack(v) for v in
                                                   cmrseq.utils.grid_sequence_list([combined_sequence, ])]
        f, a = plt.subplots(1, 1)
        a.plot(t_comb[0], adc_on_comb[0, :, 0])
        a.plot(t_comb[0], adc_on_comb[0, :, 1])
        f.savefig(f"{test_plot_output}/flash_cartesian_adcgriddin.svg")
        plt.close(f)


class TestSESequenceCartesian(unittest.TestCase):
    """ Tests for GradientEcho cartesian readout definitions"""

    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              rf_peak_power=Quantity(40, "uT"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

    def test_instantiate(self):
        echo_time = Quantity(10., "ms")
        repetition_time = Quantity(30., "ms")
        matrix_size = np.array([101, 4])
        inplane_resolution = Quantity([1, 1], "mm")
        slice_thickness = Quantity(10, "mm")
        adc_duration = Quantity(5., "ms")
        pulse_duration = Quantity(2., "ms")

        seq_list = cmrseq.seqdefs.sequences.single_line_cartesian2d(
            self.system_specs,
            echo_time=echo_time,
            repetition_time=repetition_time,
            matrix_size=matrix_size,
            inplane_resolution=inplane_resolution,
            slice_thickness=slice_thickness,
            adc_duration=adc_duration,
            pulse_duration=pulse_duration,
            time_bandwidth_product=6.)

        f, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4), gridspec_kw={"width_ratios": (3, 1)})
        seq = seq_list[0]
        seq.extend(seq_list[1:])
        cmrseq.plotting.plot_sequence(seq, axes=a1)
        cmrseq.plotting.plot_kspace_2d(seq, k_axes=(0, 1), ax=a2)
        f.suptitle("Spin Echo single line per shot")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/spin_echo_cartesian.svg")
        plt.close(f)


class TestBSSFPSequence(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.01, "ms"))

    def _plot_seq(self, seq_list, title):
        f, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={'width_ratios': (3, 1)})
        seq = seq_list[0]
        seq.extend(seq_list[1:])
        cmrseq.plotting.plot_sequence(seq, a1, format_axes=True)
        cmrseq.plotting.plot_kspace_2d(seq, k_axes=(0, 1), ax=a2)
        f.suptitle(title)
        f.tight_layout()
        return f

    def test_shortest(self):
        matrix_size = np.array([101, 4])
        inplane_resolution = Quantity([1, 1], "mm")
        slice_thickness = Quantity(10, "mm")
        adc_duration = Quantity(4., "ms")
        pulse_duration = Quantity(2., "ms")
        flip_angle = Quantity(np.pi / 2, "rad")
        TR = Quantity(0.,'ms')

        seq_list = cmrseq.seqdefs.sequences.balanced_ssfp(
            self.system_specs,
            matrix_size=matrix_size,
            inplane_resolution=inplane_resolution,
            slice_thickness=slice_thickness,
            adc_duration=adc_duration,
            flip_angle=flip_angle,
            pulse_duration=pulse_duration,
            repetition_time=TR,
            time_bandwidth_product=6.)
        f = self._plot_seq(seq_list, "BSSFP Shortest TR")
        f.savefig(f"{test_plot_output}/bssfp_shortest.svg")
        plt.close(f)

    def test_longer_than_shortest(self):
        repetition_time = Quantity(15., "ms")
        matrix_size = np.array([101, 4])
        inplane_resolution = Quantity([1, 1], "mm")
        slice_thickness = Quantity(10, "mm")
        adc_duration = Quantity(4., "ms")
        pulse_duration = Quantity(2., "ms")
        flip_angle = Quantity(np.pi / 2, "rad")

        seq_list = cmrseq.seqdefs.sequences.balanced_ssfp(
            self.system_specs,
            matrix_size=matrix_size,
            repetition_time=repetition_time,
            inplane_resolution=inplane_resolution,
            slice_thickness=slice_thickness,
            adc_duration=adc_duration,
            flip_angle=flip_angle,
            pulse_duration=pulse_duration,
            time_bandwidth_product=6.)
        f = self._plot_seq(seq_list, "BSSFP Longer TR")
        f.savefig(f"{test_plot_output}/bssfp_longer_than_shortest.svg")
        plt.close(f)

    def test_input_combinations(self):
        for i, (adc_dur, rep_time) in enumerate([(None, None), 
                                               (None, Quantity(8, "ms")),
                                               (Quantity(1.5, "ms"), None),
                                               (Quantity(3.5, "ms"), Quantity(8, "ms"))
                                               ]):
            seqs = [] 
            titles = []
            for fuse in (True, False)[:]:
                title = "Fixed TR" if rep_time is not None else "Shortest TR"
                title += ", fixed ADC-duration" if adc_dur is not None else ""
                title += ", max ADC-duration" if adc_dur is None and rep_time is not None else ""
                title += ", shortest ADC-duration" if adc_dur is None and rep_time is None else ""
                title += ", fuse" if fuse else ", no fuse"
                print("\n", title, f"{rep_time=}, {adc_dur=}")
                temp = cmrseq.seqdefs.sequences.balanced_ssfp(system_specs=self.system_specs,
                                                            matrix_size=np.array([100, 11]),
                                                            inplane_resolution=Quantity([1.5, 1.5], "mm"),
                                                            slice_thickness=Quantity(8, "mm"),
                                                            adc_duration=adc_dur,
                                                            flip_angle=Quantity(np.pi / 4, "rad"),
                                                            pulse_duration=None, #Quantity(0.8, "ms"),
                                                            repetition_time=rep_time,
                                                            slice_position_offset=Quantity(0., "m"),
                                                            time_bandwidth_product=4.,
                                                            dummy_shots=None,
                                                            fuse_slice_rewind_and_prephaser=fuse)
                print(temp[1].duration)
                seqs.append(temp[1])
                titles.append(title)

            f, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
            cmrseq.plotting.plot_sequence(seqs[0], a1, format_axes=True, add_legend=False)
            cmrseq.plotting.plot_sequence(seqs[1], a2, format_axes=True,  add_legend=False)
            a1.set_title(titles[0])
            a2.set_title(titles[1])
        f.savefig(f"{test_plot_output}/bssfp_{i}.svg")



class TestSESSEPI(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200, "mT/m/ms"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              adc_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.01, "ms"))

    def test_valid(self):
        fov = Quantity([230, 150], "mm")
        resolution = Quantity([2.35, 2.35], "mm")
        matrix_size = (fov / resolution).m.astype(int)
        echo_time = Quantity(73, "ms")
        slice_thickness = Quantity(10, "mm")
        slice_orientation = np.array([0., 0., 1.])
        pulse_duration = Quantity(2, "ms")
        tbw_product = 4.

        seq = cmrseq.seqdefs.sequences.se_ssepi(self.system_specs, field_of_view=fov,
                                                matrix_size=matrix_size, echo_time=echo_time,
                                                slice_thickness=slice_thickness,
                                                slice_orientation=slice_orientation,
                                                pulse_duration=pulse_duration,
                                                tbw_product=tbw_product, 
                                                partial_fourier_lines=0)

        f, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={'width_ratios': (3, 1)})
        cmrseq.plotting.plot_sequence(seq, a1, format_axes=True)
        cmrseq.plotting.plot_kspace_2d(seq, k_axes=(0, 1), ax=a2)
        f.savefig(f"{test_plot_output}/se_single_shot_epi_valid.svg")
        plt.close(f)
