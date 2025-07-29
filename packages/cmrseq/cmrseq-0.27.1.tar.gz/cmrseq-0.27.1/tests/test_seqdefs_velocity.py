import unittest
import os

from pint import Quantity
import numpy as np
import matplotlib.pyplot as plt

import cmrseq


test_plot_output = f"{os.path.dirname(__file__)}/output/seqdefs_velocity/"
os.makedirs(test_plot_output, exist_ok=True)


class TestVelocity(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.01, "ms"))

    def test_bipolar(self):

        with self.subTest("Test with set duration"):
            seq1 = cmrseq.seqdefs.velocity.bipolar(venc=Quantity(0.2, "m/s"),
                                                   direction=np.array([1., 0., 0.]),
                                                   duration=Quantity(5, "ms"),
                                                   system_specs=self.system_specs)
            t, wf = seq1.gradients_to_grid()
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad /
                           (sum(Quantity(wf[0], 'mT/m') * (Quantity(t, 'ms') - Quantity(t, 'ms')[int(t.size / 2) - 1])
                                * self.system_specs.grad_raster_time))).to("m/s")

            self.assertTrue(np.allclose(Quantity(0.2, "m/s"), abs(venc_actual), rtol=1e-5),
                            msg="Calculated Venc doesn't match requested, set duration")

        with self.subTest("Shortest, triangular"):
            seq2 = cmrseq.seqdefs.velocity.bipolar(venc=Quantity(30, "m/s"),
                                                   direction=np.array([1., 0., 0.]),
                                                   system_specs=self.system_specs)
            t, wf = seq2.gradients_to_grid()
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad /
                           (sum(Quantity(wf[0], 'mT/m') * (Quantity(t, 'ms') - Quantity(t, 'ms')[int(t.size / 2) - 1])
                                * self.system_specs.grad_raster_time))).to("m/s")
            self.assertTrue(np.allclose(Quantity(30, "m/s"), abs(venc_actual), rtol=1e-5),
                            msg="Calculated Venc doesn't match requested, shortest triangular")

        with self.subTest("Shortest trapezoidal"):
            seq3 = cmrseq.seqdefs.velocity.bipolar(venc=Quantity(0.2, "m/s"),
                                                   direction=np.array([1., 0., 0.]),
                                                   system_specs=self.system_specs)
            t, wf = seq3.gradients_to_grid()
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad /
                           (sum(Quantity(wf[0], 'mT/m') * (Quantity(t, 'ms') - Quantity(t, 'ms')[int(t.size / 2) - 1])
                                * self.system_specs.grad_raster_time))).to("m/s")
            self.assertTrue(np.allclose(Quantity(0.2, "m/s"), abs(venc_actual), rtol=1e-5),
                            msg="Calculated Venc doesn't match requested, shortest trap")

        with self.subTest("Arbitrary direction"):
            seq4 = cmrseq.seqdefs.velocity.bipolar(venc=Quantity(0.2, "m/s"),
                                                   direction=np.array([3., 2., 1.]),
                                                   system_specs=self.system_specs)
        subtest_titles = ["Test with set duration", "Shortest, triangular",
                          "Shortest trapezoidal", "Arbitrary direction"]

        f, a = plt.subplots(2, 2, figsize=(12, 6))
        for ax, seq, t in zip(a.flatten(), [seq1, seq2, seq3, seq4], subtest_titles):
            cmrseq.plotting.plot_sequence(seq, ax)
            ax.set_title(t)
        f.tight_layout()
        f.suptitle("bipolar venc")
        f.savefig(f"{test_plot_output}/bipolar_venc.svg")

    def test_flow_comp(self):

        with self.subTest("Trapezoidal shortest"):
            seq1 = cmrseq.seqdefs.velocity.flow_comp(venc_eff=Quantity(0.05, "m/s"),
                                                     direction=np.array([1., 0., 0.]),
                                                     repetitions=2,
                                                     system_specs=self.system_specs)
            t, wf = seq1.gradients_to_grid()
            M1_actual = np.max(
                np.cumsum(Quantity(wf[0], 'mT/m') * Quantity(t, 'ms'))) * self.system_specs.grad_raster_time
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad / M1_actual).to("m/s")

            self.assertTrue(np.allclose(Quantity(0.05, "m/s"), abs(venc_actual), rtol=1e-2),
                            msg="Calculated Venc doesn't match requested, set duration")

        with self.subTest("Hybrid, shortest"):
            seq2 = cmrseq.seqdefs.velocity.flow_comp(venc_eff=Quantity(0.1, "m/s"),
                                                     direction=np.array([1., 0., 0.]),
                                                     repetitions=3,
                                                     system_specs=self.system_specs)
            t, wf = seq2.gradients_to_grid()
            M1_actual = np.max(
                np.cumsum(Quantity(wf[0], 'mT/m') * Quantity(t, 'ms'))) * self.system_specs.grad_raster_time
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad / M1_actual).to("m/s")

            self.assertTrue(np.allclose(Quantity(0.1, "m/s"), abs(venc_actual), rtol=1e-2),
                            msg="Calculated Venc doesn't match requested, shortest triangular")

        with self.subTest("Triangular, shortest"):
            seq3 = cmrseq.seqdefs.velocity.flow_comp(venc_eff=Quantity(1, "m/s"),
                                                     direction=np.array([1., 0., 0.]),
                                                     repetitions=3,
                                                     system_specs=self.system_specs)
            t, wf = seq3.gradients_to_grid()
            M1_actual = np.max(
                np.cumsum(Quantity(wf[0], 'mT/m') * Quantity(t, 'ms'))) * self.system_specs.grad_raster_time
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad / M1_actual).to("m/s")

            self.assertTrue(np.allclose(Quantity(1, "m/s"), abs(venc_actual), rtol=1e-2),
                            msg="Calculated Venc doesn't match requested, shortest trap")

        with self.subTest("Trapezoidal, set duration"):
            seq4 = cmrseq.seqdefs.velocity.flow_comp(venc_eff=Quantity(1, "m/s"),
                                                     direction=np.array([1., 0., 0.]),
                                                     repetitions=2,
                                                     period=Quantity(2, "ms"),
                                                     system_specs=self.system_specs)
            t, wf = seq4.gradients_to_grid()
            M1_actual = np.max(
                np.cumsum(Quantity(wf[0], 'mT/m') * Quantity(t, 'ms'))) * self.system_specs.grad_raster_time
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad / M1_actual).to("m/s")

            self.assertTrue(np.allclose(Quantity(1, "m/s"), abs(venc_actual), rtol=1e-2),
                            msg="Calculated Venc doesn't match requested, set duration")

        with self.subTest("Hybrid, set duration"):
            seq5 = cmrseq.seqdefs.velocity.flow_comp(venc_eff=Quantity(0.08, "m/s"),
                                                     direction=np.array([1., 0., 0.]),
                                                     repetitions=3,
                                                     period=Quantity(2.1, "ms"),
                                                     system_specs=self.system_specs)
            t, wf = seq5.gradients_to_grid()
            M1_actual = np.max(
                np.cumsum(Quantity(wf[0], 'mT/m') * Quantity(t, 'ms'))) * self.system_specs.grad_raster_time
            venc_actual = (Quantity(np.pi, "rad") / self.system_specs.gamma_rad / M1_actual).to("m/s")

            self.assertTrue(np.allclose(Quantity(0.08, "m/s"), abs(venc_actual), rtol=1e-2),
                            msg="Calculated Venc doesn't match requested, set duration")

        with self.subTest("Arbitrary direction"):
            seq6 = cmrseq.seqdefs.velocity.flow_comp(venc_eff=Quantity(0.2, "m/s"),
                                                     repetitions=1,
                                                     direction=np.array([3., 2., 1.]),
                                                     system_specs=self.system_specs)

        subtest_titles = ["Shortest trapezoidal", "Set duration, trapezodial", "Shortest hybrid",
                          "Set duration, hybrid", "Shortest triangular", "Arbitrary direction"]
        f, a = plt.subplots(2, 3, figsize=(14, 9))
        for ax, seq, t in zip(a.flatten(), [seq1, seq4, seq2, seq5, seq3, seq6], subtest_titles):
            cmrseq.plotting.plot_sequence(seq, ax, add_legend=False)
            ax.set_title(t)
        f.tight_layout()
        f.suptitle("flow compensated venc")
        f.savefig(f"{test_plot_output}/flow_compensated.svg")