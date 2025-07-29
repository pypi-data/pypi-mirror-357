import unittest
import os

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq

test_plot_output = f"{os.path.dirname(__file__)}/output/bausteine_adc/"
os.makedirs(test_plot_output, exist_ok=True)


class TestADCphases(unittest.TestCase):
    def setUp(self) -> None:

        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.01, "ms"),
                                              adc_raster_time=Quantity(0.01, "ms"))

        amp = Quantity(20, "mT/m")
        self.trapezoid = cmrseq.bausteine.TrapezoidalGradient(
                                        self.system_specs,
                                        orientation=np.array([1., 0., 0.]),
                                        amplitude=amp,
                                        flat_duration=Quantity(2.5, "ms"),
                                        rise_time=self.system_specs.get_shortest_rise_time(amp))

    def test_grid_adc(self):
        adc = cmrseq.bausteine.GridSamplingADC(self.system_specs,
                                               duration=self.trapezoid.flat_duration,
                                               delay=self.trapezoid.rise_time,
                                               frequency_offset=Quantity(2., "Hz"),
                                               phase_offset=Quantity(0.2, "rad"))
        seq = cmrseq.Sequence([self.trapezoid, adc], self.system_specs)
        time, adc_on, phase, start_end = seq.adc_to_grid(force_raster=False)

        f, a = plt.subplots(1, 1)
        a.plot(time, phase)
        f.suptitle("GridSampling adc to grid")
        f.savefig(f"{test_plot_output}/test_grid_adc.svg")
        plt.close(f)

    def test_symmetric_adc(self):
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(
                                                self.system_specs,
                                                num_samples=31,
                                                duration=self.trapezoid.flat_duration,
                                                delay=self.trapezoid.rise_time,
                                                frequency_offset=Quantity(2., "Hz"),
                                                phase_offset=Quantity(0.2, "rad"))
        seq = cmrseq.Sequence([self.trapezoid, adc], self.system_specs)
        time, adc_on, phase, start_end = seq.adc_to_grid(force_raster=False)
        time2, adc_on, phase2, start_end = seq.adc_to_grid(force_raster=True)

        f, a = plt.subplots(1, 2)
        a[0].plot(time, phase)
        a[1].plot(time2, phase2)
        f.suptitle("GridSampling adc to grid")
        f.savefig(f"{test_plot_output}/test_symmetric_adc.svg")
        plt.close(f)


class TestADCCenter(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              grad_raster_time=Quantity(10, "us"),
                                              rf_raster_time=Quantity(1, "us"),
                                              adc_raster_time=Quantity(1, "us"))

    def test_symmetric_adc(self):
        """

        :return:
        """
        adc_even = cmrseq.bausteine.SymmetricADC.from_centered_valid(self.system_specs,
                                                 num_samples=10,
                                                 duration=Quantity(2., "ms"),
                                                 delay=Quantity(1., "ms"),
                                                 frequency_offset=Quantity(0., "Hz"),
                                                 phase_offset=Quantity(0., "rad"))
        seq_even = cmrseq.Sequence([adc_even], self.system_specs)

        adc_odd = cmrseq.bausteine.SymmetricADC.from_centered_valid(self.system_specs,
                                                                    num_samples=11,
                                                                    duration=Quantity(2., "ms"),
                                                                    delay=Quantity(1., "ms"),
                                                                    frequency_offset=Quantity(0., "Hz"),
                                                                    phase_offset=Quantity(0., "rad"))
        seq_odd = cmrseq.Sequence([adc_odd], self.system_specs)

        f, (a_even, a_odd) = plt.subplots(2, 1, sharex=True, figsize=(15, 4))
        cmrseq.plotting.plot_sequence(seq_even, axes=a_even)
        cmrseq.plotting.plot_sequence(seq_odd, axes=a_odd)
        [_.set_ylim([-1.5, 1.5]) for _ in f.axes[-2:]]
        f.suptitle("Symmetric ADC with even and odd number of samples")
        f.savefig(f"{test_plot_output}/test_symmetric_adc.svg")
        plt.close(f)
        self.assertEqual(adc_odd.adc_center, Quantity(2., "ms"))
        # For even ADC, since we have an extra sample at the start, the center is shifted by half the raster time
        self.assertLessEqual(adc_even.adc_center, Quantity(2.1, "ms"))

    def test_gridsampling_adc(self):
        adc_even = cmrseq.bausteine.GridSamplingADC(self.system_specs,
                                                    duration=Quantity(1., "ms"),
                                                    frequency_offset=Quantity(0., "Hz"),
                                                    phase_offset=Quantity(0., "rad"))
        seq_even = cmrseq.Sequence([adc_even], self.system_specs)

        adc_odd = cmrseq.bausteine.GridSamplingADC(self.system_specs,
                                                duration=Quantity(1., "ms") + self.system_specs.adc_raster_time,
                                                frequency_offset=Quantity(0., "Hz"),
                                                phase_offset=Quantity(0., "rad"))
        seq_odd = cmrseq.Sequence([adc_odd], self.system_specs)

        f, (a_even, a_odd) = plt.subplots(2, 1, sharex=True, figsize=(15, 4))
        cmrseq.plotting.plot_sequence(seq_even, axes=a_even)
        cmrseq.plotting.plot_sequence(seq_odd, axes=a_odd)
        [_.set_ylim([-1.5, 1.5]) for _ in f.axes[-2:]]
        f.suptitle("Gridsampling ADC with even and odd number of samples")
        f.savefig(f"{test_plot_output}/test_gridsampling_adc.svg")
        plt.close(f)
        assumed_adc_center = Quantity(0.5, "ms")
        self.assertTrue(np.isclose(adc_odd.adc_center, Quantity(0.501, "ms")),
                        msg=f"\n{adc_odd.adc_center=} close to \n{assumed_adc_center=}\n with "
                            f"half raster time tolerance")
        self.assertTrue(np.isclose(adc_even.adc_center, Quantity(0.5, "ms")),
                        msg=f"\n{adc_even.adc_center=} close to \n{assumed_adc_center=}\n with "
                            f"half raster time tolerance")