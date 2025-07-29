import unittest
import os

import numpy as np
import matplotlib.pyplot as plt
from pint import Quantity

import cmrseq

test_plot_output = f"{os.path.dirname(__file__)}/output/bausteine_rf/"
os.makedirs(test_plot_output, exist_ok=True)


class TestSincPulse(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              rf_peak_power=Quantity(30, "uT"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

    def test_plot(self):
        rf_sinc = cmrseq.bausteine.SincRFPulse(system_specs=self.system_specs,
                                               flip_angle=Quantity(np.pi / 2, "rad"),
                                               duration=Quantity(1., "ms"),
                                               time_bandwidth_product=4,
                                               center=0.5,
                                               apodization=0.5,
                                               phase_offset=Quantity(0., "rad"),
                                               frequency_offset=Quantity(1000., "Hz")
                                               )

        f, a = plt.subplots(1, 1, figsize=(10, 10))
        time, complex_alpha = rf_sinc.rf
        a.plot(time, complex_alpha.real, color="slategray", linewidth=8)
        a.plot(time, complex_alpha.imag, color="lightsteelblue", linewidth=8)
        a.plot(time, np.abs(complex_alpha), color="navy", linewidth=8)
        # a.plot(time, complex_alpha.real, color="lightsteelblue", linewidth=8)
        # a.plot(time, complex_alpha.imag, color=(0/255, 204/255, 255/255), linewidth=8)
        # a.plot(time, np.abs(complex_alpha), color=(106/255, 165/255, 248/255), linewidth=8)
        a.axis("off")
        # a.axvline(rf_sinc.rf_events[0].m)
        f.suptitle("Sinc pulse with frequency offset")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/test_sinc_pulse_dark.svg", transparent=True)
        f.savefig(f"{test_plot_output}/test_sinc_pulse_dark.png", transparent=True)
        plt.close(f)

    def test_get_shortest(self):
        rf_sinc = cmrseq.bausteine.SincRFPulse.from_shortest(system_specs=self.system_specs,
                                                             flip_angle=Quantity(np.pi / 2, "rad"),
                                                             time_bandwidth_product=4,
                                                             phase_offset=Quantity(60., "degree"),
                                                             frequency_offset=Quantity(0., "Hz"))
        f, a = plt.subplots(1, 1, figsize=(10, 10))
        time, complex_alpha = rf_sinc.rf
        a.plot(time, complex_alpha.real, "--")
        a.plot(time, complex_alpha.imag, "-.")
        a.plot(time, np.abs(complex_alpha), "-", linewidth=3)
        f.savefig(f"{test_plot_output}/test_shortest_sinc_pulse.png")

    def test_flip_angle_calculation(self):
        flip_angle = Quantity(90, "degree")
        f, axes = plt.subplots(2, 4, figsize=(12, 10), sharey=True)

        for phase_offset, ax in zip([-180, -90, -45, 0, 45, 135, 180, 225], axes.flatten()):
            with self.subTest(msg=f"Flip angle for phase offset: {phase_offset} degree"):
                pe = Quantity(phase_offset, "degree").to("rad")
                rf_sinc = cmrseq.bausteine.SincRFPulse(self.system_specs,
                                                       flip_angle=flip_angle,
                                                       duration=Quantity(1., "ms"),
                                                       time_bandwidth_product=4.5,
                                                       center=0.5,
                                                       apodization=0.5,
                                                       phase_offset=pe,
                                                       frequency_offset=Quantity(0., "Hz"))

                time, complex_alpha = rf_sinc.rf


                ax.plot(time, complex_alpha.real, linewidth=2.5)
                ax.plot(time, complex_alpha.imag, linewidth=1)
                ax.plot(time, np.abs(complex_alpha), '--')
                ax.set_title(f"{rf_sinc.phase_offset.m_as('degree')}")
                dt = Quantity(np.diff(time.m_as("ms")), "ms")
                resulting_alpha = np.sum(self.system_specs.gamma_rad.to("rad/ms/mT")
                                         * dt * (complex_alpha[1:] + complex_alpha[:-1]) / 2)

                abs_fa = np.abs(resulting_alpha)
                phase_fa = Quantity(np.angle(resulting_alpha.m), "rad").m_as("degree")
                abs_fa = np.round(abs_fa, decimals=15).m_as("degree")
                self.assertAlmostEqual(abs_fa, 90, places=6)
                self.assertAlmostEqual(np.mod(phase_fa, 180), np.mod(phase_offset, 180), places=6)
        f.savefig(f"{test_plot_output}/test_sinc_pulse_amp.svg")


class TestGaussPulse(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              rf_peak_power=Quantity(30, "uT"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

    def test_plot(self):
        rf_sinc = cmrseq.bausteine.GaussRFPulse(system_specs=self.system_specs,
                                                flip_angle=Quantity(np.pi / 2, "rad"),
                                                duration=Quantity(1., "ms"),
                                                center=0.5,
                                                apodization=0.5,
                                                phase_offset=Quantity(0., "rad"),
                                                frequency_offset=Quantity(1000., "Hz")
                                                )

        f, a = plt.subplots(1, 1, figsize=(10, 10))
        time, complex_alpha = rf_sinc.rf
        a.plot(time, complex_alpha.real, color="slategray", linewidth=8)
        a.plot(time, complex_alpha.imag, color="lightsteelblue", linewidth=8)
        a.plot(time, np.abs(complex_alpha), color="navy", linewidth=8)
        # a.plot(time, complex_alpha.real, color="lightsteelblue", linewidth=8)
        # a.plot(time, complex_alpha.imag, color=(0/255, 204/255, 255/255), linewidth=8)
        # a.plot(time, np.abs(complex_alpha), color=(106/255, 165/255, 248/255), linewidth=8)
        a.axis("off")
        a.axvline(rf_sinc.rf_events[0].m)
        f.suptitle("Gauss pulse with frequency offset")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/test_gauss_pulse_dark.png", transparent=True)
        plt.close(f)

    def test_get_shortest(self):
        rf_gauss = cmrseq.bausteine.GaussRFPulse.from_shortest(system_specs=self.system_specs,
                                                               flip_angle=Quantity(np.pi / 2, "rad"),
                                                               time_bandwidth_product=4,
                                                               phase_offset=Quantity(60., "degree"),
                                                               frequency_offset=Quantity(0., "Hz"))
        f, a = plt.subplots(1, 1, figsize=(10, 10))
        time, complex_alpha = rf_gauss.rf
        a.plot(time, complex_alpha.real, "--")
        a.plot(time, complex_alpha.imag, "-.")
        a.plot(time, np.abs(complex_alpha), "-", linewidth=3)
        f.savefig(f"{test_plot_output}/test_shortest_gauss_pulse.png")

class TestArbitraryRF(unittest.TestCase):
    def setUp(self):
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              rf_peak_power=Quantity(30, "uT"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

        self.rf_sinc = cmrseq.bausteine.SincRFPulse(system_specs=self.system_specs,
                                               flip_angle=Quantity(np.pi / 2, "rad"),
                                               duration=Quantity(20., "ms"),
                                               center=0.5,
                                               apodization=0.5,
                                               phase_offset=Quantity(0., "rad"),
                                               frequency_offset=Quantity(1000., "Hz"),
                                               time_bandwidth_product=11.
                                               )

    def test_init(self):
        wf = Quantity([10, 10], "uT")
        time = Quantity([0, 1], "ms")

        arb_pulse = cmrseq.bausteine.ArbitraryRFPulse(self.system_specs, name="test_arbi",
                                                      time_points=time, waveform=wf)
        dummy_seq = cmrseq.Sequence([arb_pulse], self.system_specs)
        f, a = plt.subplots(1, 1, figsize=(40, 10))
        cmrseq.plotting.plot_sequence(dummy_seq, axes=a)
        f.savefig(f"{test_plot_output}/test_arbitrary_pulse_pseudo_hard.svg", transparent=True)
        plt.close(f)

    def test_calculate_rf_center(self):
        from cmrseq.core.bausteine._rf import _calculate_rf_center
        t, wf = self.rf_sinc._rf
        center_time, center_index = _calculate_rf_center(t, wf)
        self.assertTrue(np.abs(center_time - self.rf_sinc.rf_events[0]) <=
                        self.system_specs.rf_raster_time)

    def test_calculate_bandwidth(self):
        from cmrseq.core.bausteine._rf import _calculate_bandwidth

        min_frequency_resolution=Quantity(5, "Hz")
        t, wf = self.rf_sinc._rf
        temp_t, temp_wf, bw = _calculate_bandwidth(t, wf, cut_off_percent=0.5,
                                                   min_frequency_resolution=min_frequency_resolution)
        f, a = plt.subplots(2, 1, figsize=(40, 10))
        a[0].plot(t.m, wf.m, "-")
        a[1].plot(temp_t.m[108000:112000], temp_wf[108000:112000], "-")
        [_.grid(True) for _ in a]
        f.tight_layout()
        f.savefig(f"{test_plot_output}/test_arbitrary_pulse.svg", transparent=True)
        plt.close(f)
        self.assertTrue(np.abs(self.rf_sinc.bandwidth - bw) < 2 * min_frequency_resolution,
                        msg=f"{self.rf_sinc.bandwidth} and {bw} not close enough")

    def test_calculate_flipangle(self):
        from cmrseq.core.bausteine._rf import _calculate_flipangle

        t, wf = self.rf_sinc._rf
        flip_angle = _calculate_flipangle(time=t, rf_waveform=wf,
                                          gamma_rad=self.system_specs.gamma_rad)
        self.assertTrue(np.abs(self.rf_sinc.rf_events[1] - flip_angle) < Quantity(1, "degree"),
                        msg=f"{self.rf_sinc.rf_events[1]} and {flip_angle} not close enough")


class TestAdiabaticRFPulses(unittest.TestCase):
    def test_bir4(self):
        system_specs = cmrseq.SystemSpec(rf_peak_power=Quantity(30, "uT"),
                                         rf_raster_time=Quantity(0.001, "ms"))

        duration = Quantity(0.06, "ms") + 2 * system_specs.rf_raster_time

        rf_pulse = cmrseq.bausteine.AdiabaticRFPulse.from_bir4(
                            system_specs,
                            duration=duration,
                            flip_angle=Quantity(np.pi/2, "rad"),
                            b1_amplitude=Quantity(25, "uT"),
                            beta=10, 
                            kappa=np.arctan(20),
                            phase_offset=Quantity(0, "rad"))
        seq = cmrseq.Sequence([rf_pulse,], system_specs)

        f, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
        axes[0].plot(*seq[0]._rf)
        axes[1].plot(seq[0]._rf[0], seq[0].phase_modulation)
        cmrseq.plotting.plot_sequence(seq, axes=axes[2], add_legend=False)

        f.savefig(f"{test_plot_output}/adiabatic_bir4.png")

    def test_hypsec(self):
        system_specs = cmrseq.SystemSpec(rf_peak_power=Quantity(30, "T"),
                                         rf_raster_time=Quantity(0.01, "ms"))

        duration = Quantity(10.24, "ms")

        rf_pulse = cmrseq.bausteine.AdiabaticRFPulse.from_hyperbolic_secant(
                                            system_specs, duration=duration,
                                            beta=Quantity(672*3, "rad/s"), mu=5,
                                            flip_angle=Quantity(179, "degree")
                                            # max_amplitude=Quantity(12, "uT")
                                            )
        print(rf_pulse.bandwidth)

        seq = cmrseq.Sequence([rf_pulse,], system_specs)

        f, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
        axes[0].plot(*seq[0]._rf)
        axes[1].plot(seq[0]._rf[0], seq[0].phase_modulation)
        cmrseq.plotting.plot_sequence(seq, axes=axes[2], add_legend=False, format_axes=False)
        f.axes[-1].set_ylim([-40, 40])
        f.savefig(f"{test_plot_output}/adiabatic_hypsec_2.png")


class TestSLRImplemetations(unittest.TestCase):
    def test_excitation(self):
        import sigpy.mri.rf as sigpy_rf
        system_specs = cmrseq.SystemSpec(rf_peak_power=Quantity(30, "uT"),
                                         rf_raster_time=Quantity(0.001, "ms"))

        rf_block = cmrseq.bausteine.SLRPulse(system_specs,
                                             flip_angle=Quantity(90, "degree"),
                                             pulse_duration=Quantity(2.5, "ms"),
                                             time_bandwidth_product=5,
                                             pulse_type="excitation",
                                             filter_type="least_squares",
                                             passband_ripple=0.01,
                                             stopband_ripple=0.01)

        time, signal = rf_block.rf
        f, (ax, ax1) = plt.subplots(1, 2)
        ax.plot(time.m_as("ms"), signal.m_as("uT").real, "-", color=f"C{0}")
        [a, b] = sigpy_rf.sim.abrm(signal.m_as("uT"),
                                   np.arange(-3 * 5, 3 * 5, 6 * 5 / 2000),
                                   True)
        Mxy = 2 * np.multiply(np.conj(a), b)
        ax1.plot(np.abs(Mxy), color=f"C{0}")
        f.savefig(f"{test_plot_output}/slr_excitation.png")


if __name__ == "__main__":
    unittest.main()