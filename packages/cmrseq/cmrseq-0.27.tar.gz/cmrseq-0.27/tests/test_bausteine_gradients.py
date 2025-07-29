import unittest
import os
from collections import namedtuple
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from pint import Quantity

import cmrseq
from cmrseq.core.bausteine import TrapezoidalGradient

TrapDef = namedtuple("TrapDef", ["amplitude", "flat_duration", "rise_time",
                                 "area", "duration", "slew"])

test_plot_output = f"{os.path.dirname(__file__)}/output/bausteine_gradients/"
os.makedirs(test_plot_output, exist_ok=True)


def plot_lobes(*args):
    f, a = plt.subplots(1, 1)
    a.grid(True)
    a.set_xlabel("ms"), a.set_ylabel("mT/m")
    for lobe in args:
        a.plot(lobe.gradients[0].m_as("ms"),
               lobe.gradients[1][0].m_as("mT/m"), alpha=0.5)
    a.legend(["Trap-Max", "Triag-Max", "Triag-submax"])
    return f


class TestTrapGrad(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec()
        self.orientation = np.array([1., 0., 0.])

    def _get_trapezoidal_definition(self):
        """ This gradient definition will allways be trapezoidal"""
        amplitude = self.system_specs.max_grad
        flat_duration = Quantity(1., "ms")
        rise_time = self.system_specs.minmax_risetime
        area = amplitude * (flat_duration + rise_time)
        duration = flat_duration + 2 * rise_time
        slew = amplitude / rise_time
        return TrapDef(amplitude, flat_duration, rise_time, area, duration, slew)

    def _get_maxgrad_triangle(self):
        """ Triangle with maximal gradient amplitude (depending on gradient raster time).
        Triangle is ensured by maxing slew-rate, with non-maximal gradient if the
        raster-time does not allow to reach max grad with max slew.
        """
        flat_duration = Quantity(0., "ms")
        rise_time = self.system_specs.time_to_raster(self.system_specs.minmax_risetime, "grad")
        rise_time -= self.system_specs.grad_raster_time
        amplitude = rise_time * self.system_specs.max_slew
        area = amplitude * rise_time
        duration = 2 * rise_time
        slew = amplitude / rise_time
        return TrapDef(amplitude, flat_duration, rise_time, area, duration, slew)

    def _get_submax_triangle(self):
        """ Half max amplitude and half mimmax rise time will lead to triangle"""
        flat_duration = Quantity(0., "ms")
        rise_time = self.system_specs.time_to_raster(self.system_specs.minmax_risetime / 2, "grad")
        rise_time -= self.system_specs.grad_raster_time
        amplitude = rise_time * self.system_specs.max_slew
        area = amplitude * rise_time
        duration = 2 * rise_time
        slew = amplitude / rise_time
        return TrapDef(amplitude, flat_duration, rise_time, area, duration, slew)

    def _get_infeasible_area(self):
        amplitude = Quantity(5, "mT/m")
        flat_duration = Quantity(0., "ms")
        rise_time = self.system_specs.get_shortest_rise_time(amplitude)
        area = amplitude * (flat_duration + rise_time) * 2  # This is too much area for the duration
        duration = (flat_duration + 2 * rise_time)
        slew = amplitude / rise_time
        return TrapDef(amplitude, flat_duration, rise_time, area, duration, slew)

    def _eval_results(self, lobe: TrapezoidalGradient):
        t, g = lobe.gradients[0].to("ms"), lobe.gradients[1].to("mT/m")
        area = np.sum((g[0, :-1] + g[0, 1:]) / 2 * np.diff(t))
        if t.shape[0] == 3:
            flat_duration = Quantity(0, "ms")
        else:
            flat_duration = t[2] - t[1]
        duration = t[-1] - t[0]
        rise_time = (duration - flat_duration) / 2
        amplitude = g[0, 1]
        slew = amplitude / rise_time
        return TrapDef(amplitude, flat_duration, rise_time, area, duration, slew)

    def _assert_trapezoidal(self, lobe: TrapezoidalGradient, reference_def: TrapDef):
        """ Collections of assertions for a trapezoidal gradient lobe"""
        lobe_def = self._eval_results(lobe)
        self.assertTrue(np.isclose(reference_def.area.m_as("mT/m*ms"),
                                   lobe_def.area.m_as("mT/m*ms"), rtol=1e-6))
        self.assertTrue(np.isclose(reference_def.slew.m_as("mT/m/ms"),
                                   lobe_def.slew.m_as("mT/m/ms"), rtol=1e-6))
        self.assertTrue(lobe_def.flat_duration.m_as("ms") > 0.)
        self.assertEqual(lobe_def.flat_duration.m_as("ms"), reference_def.flat_duration.m_as("ms"))

    def _assert_max_triangle(self, lobe: TrapezoidalGradient, reference_def: TrapDef):
        """ Collections of assertions for a triangular gradient lobe with max amplitude"""
        lobe_def = self._eval_results(lobe)
        self.assertTrue(np.isclose(reference_def.area.m_as("mT/m*ms"),
                                   lobe_def.area.m_as("mT/m*ms"), rtol=1e-6))
        self.assertTrue(np.isclose(reference_def.slew.m_as("mT/m/ms"),
                                   lobe_def.slew.m_as("mT/m/ms"), rtol=1e-6))
        self.assertTrue(lobe_def.flat_duration.m_as("ms") == 0.)
        self.assertEqual(lobe_def.duration.m_as("ms"), 2 * reference_def.rise_time.m_as("ms"))

    def _assert_submax_triangle(self, lobe: TrapezoidalGradient, reference_def: TrapDef):
        lobe_def = self._eval_results(lobe)
        self.assertTrue(lobe_def.flat_duration.m_as("ms") == 0.)
        self.assertEqual(lobe_def.duration.m_as("ms"), 2 * reference_def.rise_time.m_as("ms"))
        self.assertEqual(lobe_def.amplitude.m_as("mT/m"), reference_def.amplitude.m_as("mT/m"))

    def test_correct_start_trap(self):
        """ Test if start and end point of gradient have zero amplitude """
        l1 = TrapezoidalGradient(system_specs=self.system_specs,
                                 orientation=np.array([1., 0., 0.]),
                                 amplitude=Quantity(40, "mT/m"),
                                 flat_duration=Quantity(10, "ms"),
                                 rise_time=Quantity(1, "ms"))
        t, g = l1.gradients
        self.assertTrue(np.allclose(g[:, 0], 0, rtol=1e-10),
                        msg="First gridded sample is not zero")
        self.assertTrue(np.allclose(g[:, -1], 0, rtol=1e-10),
                        msg="Last gridded sample is not zero")

        with self.subTest(msg="Plotting waveform"):
            f, a = plt.subplots(1, 1)
            a.plot(t, *g)
            a.grid(True)
            f.suptitle("Single Trapezoid: Correct start/end")
            f.savefig(f"{test_plot_output}/test_correct_start_trap.png")
            plt.close(f)

    def test_from_area(self):
        with self.subTest(msg="Must be Trapezoidal"):
            trap_def = self._get_trapezoidal_definition()
            lobe_1 = TrapezoidalGradient.from_area(system_specs=self.system_specs,
                                                   orientation=self.orientation, area=trap_def.area)
            self._assert_trapezoidal(lobe_1, trap_def)

        with self.subTest(msg="Max gradient triangle"):
            trap_def = self._get_maxgrad_triangle()
            lobe_2 = TrapezoidalGradient.from_area(system_specs=self.system_specs,
                                                   orientation=self.orientation, area=trap_def.area)
            self._assert_max_triangle(lobe_2, trap_def)

        with self.subTest(msg="Sub maximal gradient triangle"):
            trap_def = self._get_submax_triangle()
            lobe_3 = TrapezoidalGradient.from_area(system_specs=self.system_specs,
                                                 orientation=self.orientation, area=trap_def.area)
            self._assert_submax_triangle(lobe_3, trap_def)

        with self.subTest(msg="Plotting all waveforms"):
            f = plot_lobes(lobe_1, lobe_2, lobe_3)
            f.suptitle("Trapezoidal.from_area()")
            f.savefig(f"{test_plot_output}/test_from_area.svg")
            plt.close(f)

    def test_from_dur_area(self):
        with self.subTest(msg="Must be Trapezoidal"):
            trap_def = self._get_trapezoidal_definition()
            lobe_1 = TrapezoidalGradient.from_dur_area(self.system_specs, self.orientation,
                                                    area=trap_def.area, duration=trap_def.duration)
            self._assert_trapezoidal(lobe_1, trap_def)

        with self.subTest(msg="Max gradient triangle"):
            trap_def = self._get_maxgrad_triangle()
            lobe_2 = TrapezoidalGradient.from_dur_area(self.system_specs, self.orientation,
                                                       area=trap_def.area, duration=trap_def.duration)
            self._assert_max_triangle(lobe_2, trap_def)

        with self.subTest(msg="Sub maximal gradient triangle"):
            trap_def = self._get_submax_triangle()
            lobe_3 = TrapezoidalGradient.from_dur_area(self.system_specs, self.orientation,
                                                    area=trap_def.area, duration=trap_def.duration)
            self._assert_submax_triangle(lobe_3, trap_def)

        with self.subTest(msg="Duration too short for area"):
            trap_def = self._get_infeasible_area()

            def _test():
                TrapezoidalGradient.from_dur_area(self.system_specs, self.orientation,
                                                  area=trap_def.area, duration=trap_def.duration)
            self.assertRaises(ValueError, _test)

        with self.subTest(msg="Plotting all waveforms"):
            f = plot_lobes(lobe_1, lobe_2, lobe_3)
            f.suptitle("Trapezoidal.from_dur_area()")
            f.savefig(f"{test_plot_output}/test_from_dur_area.svg")
            plt.close(f)

    def test_from_fdur_area(self):
        with self.subTest(msg="Must be Trapezoidal"):
            trap_def = self._get_trapezoidal_definition()
            lobe_1 = TrapezoidalGradient.from_fdur_area(self.system_specs, self.orientation,
                                        area=trap_def.area, flat_duration=trap_def.flat_duration)
            self._assert_trapezoidal(lobe_1, trap_def)

        with self.subTest(msg="Max gradient triangle"):
            trap_def = self._get_maxgrad_triangle()
            lobe_2 = TrapezoidalGradient.from_fdur_area(self.system_specs, self.orientation,
                                        area=trap_def.area, flat_duration=trap_def.flat_duration)
            print(f"{self._eval_results(lobe_2)}", f"{trap_def}", sep="\n")
            self._assert_max_triangle(lobe_2, trap_def)

        with self.subTest(msg="Sub maximal gradient triangle"):
            trap_def = self._get_submax_triangle()
            lobe_3 = TrapezoidalGradient.from_fdur_area(self.system_specs, self.orientation,
                                        area=trap_def.area, flat_duration=trap_def.flat_duration)
            self._assert_submax_triangle(lobe_3, trap_def)

        with self.subTest(msg="Duration too short for area"):
            def _test():
                TrapezoidalGradient.from_fdur_area(self.system_specs, self.orientation,
                        area=2*(self.system_specs.max_grad * self.system_specs.minmax_risetime),
                        flat_duration=Quantity(0, "ms"))
            self.assertRaises(ValueError, _test)

        with self.subTest(msg="Plotting all waveforms"):
            f = plot_lobes(lobe_1, lobe_2, lobe_3)
            f.suptitle("Trapezoidal.from_fdur_area()")
            f.savefig(f"{test_plot_output}/test_from_fdur_area.svg")
            plt.close(f)

    def test_from_dur_amp(self):
        with self.subTest(msg="Must be Trapezoidal"):
            trap_def = self._get_trapezoidal_definition()
            lobe_1 = TrapezoidalGradient.from_dur_amp(self.system_specs, self.orientation,
                                                      amplitude=trap_def.amplitude,
                                                      duration=trap_def.duration)
            self._assert_trapezoidal(lobe_1, trap_def)

        with self.subTest(msg="Max gradient triangle"):
            trap_def = self._get_maxgrad_triangle()
            lobe_2 = TrapezoidalGradient.from_dur_amp(self.system_specs, self.orientation,
                                                      amplitude=trap_def.amplitude,
                                                      duration=trap_def.duration)
            self._assert_max_triangle(lobe_2, trap_def)

        with self.subTest(msg="Sub max triangle with off-raster rise-time"):
            system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                             max_slew=Quantity(200., "mT/m/ms"),
                                             grad_raster_time=Quantity(0.01, "ms"),
                                             rf_raster_time=Quantity(0.01, "ms"),
                                             adc_raster_time=Quantity(0.01, "ms"),
                                             rf_peak_power=Quantity(20, 'uT'))

            self.assertRaises(cmrseq.err.BuildingBlockArgumentError,
                              lambda: cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(
                                  system_specs=system_specs, orientation=np.array([1., 0., 0.]),
                                  duration=Quantity(0.31, 'ms'), amplitude=Quantity(31, 'mT/m'))
                              )

        with self.subTest(msg="Sub maximal gradient triangle"):
            trap_def = self._get_submax_triangle()
            lobe_3 = TrapezoidalGradient.from_dur_amp(self.system_specs, self.orientation,
                                                      amplitude=trap_def.amplitude,
                                                      duration=trap_def.duration)
            self._assert_submax_triangle(lobe_3, trap_def)

        with self.subTest(msg="Duration too short for area"):
            def _test():
                TrapezoidalGradient.from_dur_amp(self.system_specs, self.orientation,
                                                 amplitude=self.system_specs.max_grad,
                                                 duration=self.system_specs.minmax_risetime)
            self.assertRaises(ValueError, _test)

        with self.subTest(msg="Plotting all waveforms"):
            f = plot_lobes(lobe_1, lobe_2, lobe_3)
            f.suptitle("Trapezoidal.from_dur_amp()")
            f.savefig(f"{test_plot_output}/from_dur_amp.svg")
            plt.close(f)

    def test_zero_amplitude(self):
        """ Test if clean_gradients removes redundant gradients"""
        lobe = TrapezoidalGradient(self.system_specs, self.orientation,
                                   amplitude=Quantity(0., "mT/m"), rise_time=Quantity(0., "ms"),
                                   flat_duration=Quantity(1., "ms"))
        self.assertTrue(len(lobe.gradients[0]) == 2)
        lobe = TrapezoidalGradient.from_dur_amp(self.system_specs, self.orientation,
                                                amplitude=Quantity(0., "mT/m"),
                                                duration=Quantity(1., "ms"))
        self.assertTrue(len(lobe.gradients[0]) == 2)

    def test_rotation(self):
        """Tests if rotation of gradients works for correctly constructed rotation matrices"""
        lobe_amp = Quantity(40, "mT/m")
        fdur, rise_t = Quantity(3, "ms"), Quantity(0.5, "ms")
        ref_area = (rise_t + fdur) * lobe_amp

        lobex = TrapezoidalGradient(self.system_specs, orientation=np.array([1., 0., 0]),
                                    name="trap_x", amplitude=lobe_amp, flat_duration=fdur,
                                    rise_time=rise_t)
        lobey = TrapezoidalGradient(self.system_specs, orientation=np.array([0., 1., 0]),
                                    name="trap_y", amplitude=lobe_amp, flat_duration=fdur,
                                    rise_time=rise_t)

        rot_swap_xy = np.array([[0., 1., 0.], [1., 0., 0.], [0., 0., 1]])
        lxr, lyr = deepcopy(lobex), deepcopy(lobey)
        lxr.rotate_gradients(rot_swap_xy)
        lyr.rotate_gradients(rot_swap_xy)
        self.assertTrue(np.allclose(lobex.gradients[1], lyr.gradients[1]))
        self.assertTrue(np.allclose(lobey.gradients[1], lxr.gradients[1]))

        rot_45_xy = np.array([[1., 1., 0.], [1., -1., 0.], [0., 0., 1]])
        rot_45_xy_normed = rot_45_xy / np.linalg.norm(rot_45_xy, axis=0, keepdims=True)
        lxr, lyr = deepcopy(lobex), deepcopy(lobey)
        lxr.rotate_gradients(rot_45_xy_normed)
        lyr.rotate_gradients(rot_45_xy_normed)
        self.assertTrue(np.allclose(lxr.area[:2], ref_area/np.sqrt(2)))
        self.assertTrue(np.allclose(lyr.area[:2], ref_area/np.sqrt(2)))

        invalid_rotation_matrix = np.array([[1., 1., 0.], [1., 0., 0.], [0., 0., 1]])
        self.assertRaises(ValueError, lambda: lxr.rotate_gradients(invalid_rotation_matrix))

    def test_area(self):
        lobe_amp = Quantity(40, "mT/m")
        fdur, rise_t = Quantity(3.5, "ms"), self.system_specs.get_shortest_rise_time(lobe_amp)
        init_orientation = np.array([1., 0., 0])
        reference_area = (fdur + rise_t) * lobe_amp * init_orientation

        lobe = TrapezoidalGradient(self.system_specs, orientation=init_orientation, name="trap_x",
                                   amplitude=lobe_amp, flat_duration=fdur, rise_time=rise_t)

        lobe2 = TrapezoidalGradient.from_fdur_area(self.system_specs, init_orientation, fdur,
                                                   reference_area[0])
        lobe3 = TrapezoidalGradient.from_dur_area(self.system_specs, init_orientation,
                                                  fdur+2*rise_t, reference_area[0])
        self.assertTrue(np.allclose(reference_area, lobe.area))
        self.assertTrue(np.allclose(reference_area, lobe2.area))
        self.assertTrue(np.allclose(reference_area, lobe3.area))


class TestArbitaryGradient(unittest.TestCase):
    def test_from_kspace(self):
        import math
        t = np.linspace(0, 1, 1000)
        ktraj = Quantity(np.stack([np.sin(2*math.pi*t), np.cos(2*math.pi*t), t],
                                  axis=-1) * 100, "1/m")
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(36, "mT/m"),
                                         max_slew=Quantity(80, "mT/m/ms"),
                                         grad_raster_time=Quantity(10, "us"))
        block = cmrseq.bausteine.ArbitraryGradient.from_kspace_trajectory(system_specs,
                                                                          kspace_traj=ktraj)
        seq = cmrseq.Sequence([block], system_specs)
        time, grad = block.gradients
        slew = np.diff(grad, axis=1) / np.diff(time)[np.newaxis]
        plt.switch_backend("agg")
        f, axes = plt.subplots(1, 3, constrained_layout=True, figsize=(12, 5),
                               width_ratios=(0.3, 0.3, 0.4))
        axes[0].plot(time[:], grad.T)
        axes[1].plot(time[:-1], slew.T)
        a2 = cmrseq.plotting.plot_kspace_3d(seq, plot_raster_trajectory=True, axis=None)
        a2.figure.canvas.draw()
        buf = a2.figure.canvas.tostring_rgb()
        ncols, nrows = a2.figure.canvas.get_width_height()
        image = np.frombuffer(buf, dtype=np.uint8).reshape(nrows, ncols, 3)
        axes[2].imshow(image)
        axes[2].axis("off")
        [a.set_title(t) for (a, t) in zip(axes, ("Gradient", "Slew Rate", "k-space"))]
        f.savefig(f"{test_plot_output}/arbitrary_from_kspace.png")


if __name__ == "__main__":
    unittest.main()
