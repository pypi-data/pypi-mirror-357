import unittest
from copy import deepcopy
import os

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq

test_plot_output = f"{os.path.dirname(__file__)}/output/plotting/"
os.makedirs(test_plot_output, exist_ok=True)

class TestWaveformPlots(unittest.TestCase):
    """ Tests covering the sequence composition functionality"""
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec()
        self.rf = cmrseq.bausteine.SincRFPulse.from_shortest(self.system_specs,
                                                             Quantity(45, "degree"))
        self.grad = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(self.system_specs,
                                                                       np.array([1., 2, 3]),
                                                                       flat_duration=Quantity(1, "ms"),
                                                                       amplitude=Quantity(10, "mT/m"))
        self.adc = cmrseq.bausteine.SymmetricADC(self.system_specs, num_samples=100,
                                                 dwell=Quantity(40, "us"))

        seq = cmrseq.Sequence([], self.system_specs)
        seq.extend([self.rf, self.grad, self.adc])
        self.combined_seq = seq

    def test_raise_exceptions(self):
        with self.subTest("Faulty fig creations arguments"):
            self.assertRaises(NotImplementedError, lambda : cmrseq.plotting.plot_sequence(self.combined_seq, axes="fdg;kjfgfg"))
            self.assertRaises(NotImplementedError, lambda: cmrseq.plotting.plot_sequence(self.combined_seq, axes="perchannel", gradient_style="asgagd"))
            self.assertRaises(NotImplementedError, lambda : cmrseq.plotting.plot_kspace_2d(self.combined_seq, map_sampling_times="dsfgasdg"))
            self.assertRaises(NotImplementedError, lambda: cmrseq.plotting.plot_moment(self.combined_seq,
                                                                                axes="fdg;kjfgfg"))

    def test_plot_combined(self):
        fig = cmrseq.plotting.plot_sequence(self.combined_seq, axes="single", add_flip_angles=True)
        fig.savefig(f"{test_plot_output}/plot_combined_0.svg")

        fig = cmrseq.plotting.plot_sequence(self.combined_seq, axes="single", add_flip_angles=True,
                                            gradient_style="filled")
        fig.savefig(f"{test_plot_output}/plot_combined_1.svg")

        fig = cmrseq.plotting.plot_sequence(self.combined_seq, axes="single", add_flip_angles=True,
                                            gradient_style="hatched_/")
        [cmrseq.plotting.center_axes(ax, ticksoff="xy") for ax in fig.axes]
        fig.savefig(f"{test_plot_output}/plot_combined_2.svg")

        fig = cmrseq.plotting.plot_moment(self.combined_seq, axes="single")
        fig.savefig(f"{test_plot_output}/plot_combined_3.svg")

        fig = cmrseq.plotting.plot_moment(self.combined_seq, axes="perchannel")
        fig.savefig(f"{test_plot_output}/plot_combined_4.svg")

        fig = cmrseq.plotting.plot_moment(self.combined_seq, axes=None)
        fig.savefig(f"{test_plot_output}/plot_combined_5.svg")

        fig, axes = plt.subplots(1, 1)
        cmrseq.plotting.plot_moment(self.combined_seq, axes=(axes, axes, axes))

        ax = cmrseq.plotting.plot_kspace_2d(self.combined_seq, ax=None, map_sampling_times="global")
        ax.figure.savefig(f"{test_plot_output}/plot_kspace_1.svg")
        ax = cmrseq.plotting.plot_kspace_2d(self.combined_seq, ax=None,
                                             map_sampling_times="relative")
        cmrseq.plotting.center_axes(ax, ticksoff="xy")
        ax.figure.savefig(f"{test_plot_output}/plot_kspace_2.svg")

        ax = cmrseq.plotting.plot_kspace_3d(self.combined_seq)
        ax.figure.savefig(f"{test_plot_output}/plot_kspace_3.svg")

        fig = cmrseq.plotting.plot_gradient_spectra(self.combined_seq, directions=None)
        fig = cmrseq.plotting.plot_gradient_spectra(self.combined_seq, directions=np.eye(3, 3))
