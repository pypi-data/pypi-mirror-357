import unittest

import numpy as np
import os
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq


test_plot_output = f"{os.path.dirname(__file__)}/output/seqdefs_excitation/"
os.makedirs(test_plot_output, exist_ok=True)

class TestMultiband(unittest.TestCase):
    def setUp(self):
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(100., "mT/m/ms"),
                                              rf_peak_power=Quantity(30, "uT"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.005, "ms"))

        self.single_sinc = cmrseq.bausteine.SincRFPulse(self.system_specs,
                                                        duration=Quantity(2.5, "ms"),
                                                        flip_angle=Quantity(np.pi/2, "rad"),
                                                        time_bandwidth_product=4.)
        #
        # self.single_sinc = cmrseq.bausteine.SLRPulse(self.system_specs,
        #                                              flip_angle=Quantity(90, "degree"),
        #                                              pulse_duration=Quantity(512 * 0.005, "ms"),
        #                                              pulse_type="excitation",
        #                                              filter_type="sinc",
        #                                              time_bandwidth_product=8.)

    def _simulate_1d_profile(self, pulse: cmrseq.bausteine.RFPulse, range_factor: float = 5):
        import sigpy.mri.rf as sigpy_rf
        tb_product = pulse.bandwidth.m_as("kHz") * pulse.duration.m_as("ms")

        pulse = pulse.rf[1].m_as("T").real * 10_000 / 2 / np.pi
        tmp = range_factor * tb_product
        [a, b] = sigpy_rf.sim.abrm(pulse, np.arange(- tmp, tmp, 2 * tmp / 2000), False)
        Mxy = 2 * np.multiply(np.conj(a), b)
        return Mxy
    def test_sms_sinc(self):
        sim_fac = 8
        sms_pulses = []
        transverse_mags = []
        for mod_type in ("amplitude", "phase", "quadrature"):
            tmp_sms = cmrseq.seqdefs.excitation.sms_pulse(self.system_specs,
                                                           single_pulse=self.single_sinc,
                                                           n_slices=4,
                                                           band_gap=Quantity(30, "mm"),
                                                           slice_thickness=Quantity(10, "mm"),
                                                           modulation_type=mod_type)
            sms_pulses.append(tmp_sms)
            transverse_mags.append(self._simulate_1d_profile(tmp_sms, sim_fac))

        Mxy_single = self._simulate_1d_profile(self.single_sinc, sim_fac)



        f, axes = plt.subplots(2, 4, sharey="row", sharex="row",
                               figsize=(17, 6), constrained_layout=True)
        axes[0, 0].plot(self.single_sinc.rf[0].m_as("ms"), self.single_sinc.rf[1].m_as("uT").real)
        axes[0, 0].plot(self.single_sinc.rf[0].m_as("ms"), self.single_sinc.rf[1].m_as("uT").imag)
        axes[1, 0].plot(np.abs(Mxy_single))
        for col_idx, mxy, pulse in zip(range(1, 4), transverse_mags, sms_pulses):
            axes[0, col_idx].plot(pulse.rf[0].m_as("ms"), pulse.rf[1].m_as("uT").real)
            axes[0, col_idx].plot(pulse.rf[0].m_as("ms"), pulse.rf[1].m_as("uT").imag)
            axes[1, col_idx].plot(np.abs(mxy))

        [a.set_title(t) for a, t in zip(axes[0], ["Single Slice", "Amplitude modulation",
                                                  "Phase modulation", "Quadrature modulation"])]
        axes[0, 0].set_ylabel
        # cmrseq.plotting.plot_sequence(seq1, axes=a)
        f.savefig(f"{test_plot_output}/sms_sinc_pulse.png")
        plt.close(f)


class TestExcitation(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              rf_peak_power=Quantity(40, "uT"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.005, "ms"))

    def test_slice_selective_pulse(self):
        seq1 = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                    slice_thickness=Quantity(15., "mm"),
                    flip_angle=Quantity(np.pi / 2, "rad"),
                    pulse_duration=Quantity(2., "ms"),
                    time_bandwidth_product=6.,
                    delay=Quantity(0., "ms"),
                    slice_position_offset=Quantity(1, "cm"),
                    slice_normal=np.array([0., 0., 1.]),
                    system_specs=self.system_specs)

        f, a = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
        cmrseq.plotting.plot_sequence(seq1, axes=a[0])
        cmrseq.plotting.plot_block_names(seq1, axis=a[1])
        f.suptitle("Slice selective Excitation with slice-position offset")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/slice_selective_pulse.svg")

        plt.close(f)

    def test_slice_selective_se_pair(self):
        TE = Quantity(15, "ms")
        seq1 = cmrseq.seqdefs.excitation.slice_selective_se_pulses(
                                                self.system_specs,
                                                echo_time=TE,
                                                slice_thickness=Quantity(10, "mm"),
                                                pulse_duration=Quantity(2., "ms"),
                                                slice_orientation=np.array([0., 0., 1]),
                                                time_bandwidth_product=6.)
        self.assertTrue(np.isclose((seq1.rf_events[1][0] - seq1.rf_events[0][0]), TE/2))

        f, a = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
        cmrseq.plotting.plot_sequence(seq1, axes=a[0])
        cmrseq.plotting.plot_block_names(seq1, axis=a[1])

        f.suptitle("Slice selective Excitation pair for Spin echo")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/test_slice_selective_se_pair.svg")
        plt.close(f)


class Test2DRF(unittest.TestCase):
    def test_navigator(self):
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(100., "mT/m/ms"),
                                              rf_peak_power=Quantity(40, "uT"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.005, "ms"))
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy import special



        special.jv