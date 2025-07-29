import unittest
from copy import deepcopy
import os

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq


test_plot_output = f"{os.path.dirname(__file__)}/output/omatrix/"
os.makedirs(test_plot_output, exist_ok=True)


class TestOMatrix(unittest.TestCase):
    def test_apply_gradient(self):
        system_specs = cmrseq.SystemSpec()
        trap1 = cmrseq.bausteine.TrapezoidalGradient(system_specs, orientation=np.array([0., 0., 1.]),
                                                     amplitude=Quantity(10, "mT/m"),
                                                     flat_duration=Quantity(1, "ms"),
                                                     rise_time=Quantity(0.1, "ms"))
        omatrix = cmrseq.OMatrix(Quantity(0., "m"),
                                 slice_normal=np.array([1., 2., 0.]),
                                 readout_direction=np.array([0., 0., 1.]),
                                 system_specs=system_specs)
        print(omatrix.tmatrix)
        t, g = omatrix._apply_gradient(trap1)

        fig, axes = plt.subplots(1, 1)
        axes.plot(t, g.T)
        fig.savefig(f"{test_plot_output}/test_apply_matrix_grad.png")

    def test_apply_rf(self):
        system_specs = cmrseq.SystemSpec(rf_raster_time=Quantity(1, "us"))
        seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(system_specs,
                                                                   slice_thickness=Quantity(10, "mm"),
                                                                   flip_angle=Quantity(10, "degree"),
                                                                   time_bandwidth_product=4,
                                                                   pulse_duration=None,
                                                                   slice_normal=np.array([0., 0., 1.])
                                                                   )
        omatrix = cmrseq.OMatrix(Quantity(1., "cm"),
                                 slice_normal=np.array([1., 2., 0.]),
                                 readout_direction=np.array([0., 0., 1.]),
                                 system_specs=system_specs)

        t, wf = omatrix._apply_rf(seq[1], seq[0])
        tg, wfg = omatrix._apply_gradient(seq[0])
        fig, axes = plt.subplots(1, 1)
        axes.plot(t, wf.real, "-", color="purple")
        axes.plot(t, wf.imag, "--", color="purple")
        axes.plot(tg, wfg.T)
        fig.savefig(f"{test_plot_output}/test_apply_matrix_rf.png")



if __name__ == '__main__':
    unittest.main()
