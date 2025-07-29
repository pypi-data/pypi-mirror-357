import unittest
from copy import deepcopy
import os

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq


test_plot_output = f"{os.path.dirname(__file__)}/output/sequence/"
os.makedirs(test_plot_output, exist_ok=True)


class TestSequenceComposition(unittest.TestCase):
    """ Tests covering the sequence composition functionality"""
    def test_addition(self):
        system_specs1 = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                          max_slew=Quantity(200., "mT/m/ms"),
                                          grad_raster_time=Quantity(0.01, "ms"),
                                          rf_raster_time=Quantity(0.01, "ms"),
                                          adc_raster_time=Quantity(0.001, "ms"))
        system_specs2 = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                          max_slew=Quantity(200., "mT/m/ms"),
                                          grad_raster_time=Quantity(0.02, "ms"),
                                          rf_raster_time=Quantity(0.01, "ms"),
                                          adc_raster_time=Quantity(0.001, "ms"))
        l1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=system_specs1,
                                                  orientation=np.array([1., 0., 0.]),
                                                  amplitude=Quantity(20, "mT/m"),
                                                  duration=Quantity(1., "ms"))
        l2 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=system_specs1,
                                                  orientation=-np.array([1., 0., 0.]),
                                                  amplitude=Quantity(20, "mT/m"),
                                                  duration=Quantity(1., "ms"))
        seq1 = cmrseq.Sequence([l1], system_specs1)
        seq11 = cmrseq.Sequence([l2], system_specs1)
        seq2 = cmrseq.Sequence([l2], system_specs2)

        with self.subTest("Addition of identical sequences"):
            seq3 = seq1 + seq11
            t, wf = seq3.gradients_to_grid()
            self.assertEqual(wf.sum(), 0.)

        with self.subTest("Addition of non-matching sequences"):
            self.assertRaises(ValueError, lambda: seq1 + seq2)

        with self.subTest("Inplace addition"):
            seq1 += seq11

        print(seq1.blocks)
        print([b.name for b in seq1])
        print({k: b.name for k, b in seq1.items()})


    def test_addblock(self):

        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"),
                                         adc_raster_time=Quantity(0.001, "ms"))
        l1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(
                                        system_specs=system_specs,
                                        orientation=np.array([1., 0., 0.]),
                                        amplitude=Quantity(20, "mT/m"),
                                        duration=Quantity(1., "ms"))
        seq1 = cmrseq.Sequence([l1], system_specs)

        with self.subTest("add valid block with copy"):
            seq_dum = deepcopy(seq1)
            seq_dum.add_block(l1, copy=True)
            self.assertEqual(seq_dum.duration, seq1.duration)
            self.assertEqual(np.max(np.abs(seq_dum.gradients_to_grid()[1])),
                             2 * np.max(np.abs(seq1.gradients_to_grid()[1])))

        with self.subTest("Invalid block type"):
            seq_dum = deepcopy(seq1)
            self.assertRaises(NotImplementedError, lambda : seq_dum.add_block(1))

        with self.subTest("Invalid block system specs"):
            lerr = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(
                system_specs=cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                               max_slew=Quantity(200., "mT/m/ms"),
                                               grad_raster_time=Quantity(0.005, "ms"),
                                               rf_raster_time=Quantity(0.005, "ms"),
                                               adc_raster_time=Quantity(0.001, "ms")),
                orientation=-np.array([1., 0., 0.]),
                amplitude=Quantity(20, "mT/m"),
                duration=Quantity(1.005, "ms"))
            seq_dum = deepcopy(seq1)
            self.assertRaises(ValueError, lambda: seq_dum.add_block(lerr))


class TestSequenceOMatrix(unittest.TestCase):
    def test_gradients_only(self):
        system_specs = cmrseq.SystemSpec()
        trap1 = cmrseq.bausteine.TrapezoidalGradient(system_specs, orientation=np.array([0., 0., 1.]),
                                                     amplitude=Quantity(10, "mT/m"),
                                                     flat_duration=Quantity(0.5, "ms"),
                                                     rise_time=Quantity(0.1, "ms"),
                                                     delay=Quantity(0.2, "ms"))
        trap2 = cmrseq.bausteine.TrapezoidalGradient(system_specs,
                                                     orientation=np.array([1., 0., 0.]),
                                                     amplitude=Quantity(10, "mT/m"),
                                                     flat_duration=Quantity(1, "ms"),
                                                     rise_time=Quantity(0.1, "ms"),
                                                     delay=trap1.tmax)
        trap3 = cmrseq.bausteine.TrapezoidalGradient(system_specs,
                                                     orientation=np.array([1., 1., 1.]),
                                                     amplitude=Quantity(10, "mT/m"),
                                                     flat_duration=Quantity(0., "ms"),
                                                     rise_time=Quantity(0.1, "ms"))
        sequence = cmrseq.Sequence([trap3, trap1, trap2], system_specs)

        omatrix = cmrseq.OMatrix(Quantity(0., "m"),
                                 slice_normal=np.array([1., 2., 0.]),
                                 readout_direction=np.array([0., 0., 1.]),
                                 system_specs=system_specs)
        sequence.register_omatrix(omatrix, gradients=sequence.blocks[1:])

        fig, ax = plt.subplots(3, 1, sharex=True, sharey=True)
        for t, g in sequence.gradients:
            _ = [a.plot(t, gg) for gg, a in zip(g, ax)]
        fig.savefig(f"{test_plot_output}/sequence_omatrix_gradients.png")

    def test_rf_only(self):
        system_specs = cmrseq.SystemSpec()
        sequence = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(system_specs,
                                                                   slice_thickness=Quantity(10, "mm"),
                                                                   flip_angle=Quantity(40, "degree"),
                                                                   time_bandwidth_product=4,
                                                                   pulse_duration=None)

        omatrix = cmrseq.OMatrix(Quantity(2., "cm"),
                                 slice_normal=np.array([1., 2., 0.]),
                                 readout_direction=np.array([0., 0., 1.]),
                                 system_specs=system_specs)

        sequence.register_omatrix(omatrix, gradients=[sequence[0], sequence[2]],
                                  rf_pulses=[(sequence[1], sequence[0]), ])
        fig, ax = plt.subplots(4, 1, sharex=True, sharey=True)
        t, rfwf = sequence.rf[0]
        ax[0].plot(t, rfwf.real, "-", color="purple")
        ax[0].plot(t, rfwf.imag, "--", color="purple")
        for t, g in sequence.gradients:
            _ = [a.plot(t, gg) for gg, a in zip(g, ax[1:])]
        fig.savefig(f"{test_plot_output}/sequence_omatrix_rf.png")

class TestGradientGridding(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                             max_slew=Quantity(200., "mT/m/ms"),
                                             grad_raster_time=Quantity(0.01, "ms"),
                                             rf_raster_time=Quantity(0.01, "ms"))

    def test_gridding_trapezoidals(self):
        l1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=self.system_specs,
                                                               orientation=np.array([1., 0., 0.]),
                                                               amplitude=Quantity(20, "mT/m"),
                                                               duration=Quantity(10, "ms"),
                                                               delay=Quantity(1.5, "ms"))

        l3 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=self.system_specs,
                                                               orientation=np.array([0., 2., 1.]),
                                                               amplitude=Quantity(5, "mT/m"),
                                                               duration=Quantity(26, "ms"),
                                                               delay=Quantity(1.5, "ms"))

        seq = cmrseq.Sequence([l1, l3], system_specs=self.system_specs)

        with self.subTest("Dense gridding"):
            t, wf = seq.gradients_to_grid()
        
        with self.subTest("Sparse gridding"):
            t, wf = seq.combined_gradients()
            fig, ax = plt.subplots(1, 1, constrained_layout=True)
            ax.plot(t, wf.T, "x-")
            fig.savefig(f"{test_plot_output}/sparse_grad_gridding.png")
            plt.close(fig)

    def test_gridding_empty_sequence(self):
        dummyseq = cmrseq.Sequence([], self.system_specs)
        with self.subTest("Dense gridding"):
            t, wf = dummyseq.gradients_to_grid()
            self.assertTrue(all([t is None, wf is None]))

        with self.subTest("Sparse gridding"):
            t, wf = dummyseq.combined_gradients()


class TestRFGridding(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                              max_slew=Quantity(200., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.01, "ms"),
                                              rf_peak_power=Quantity(30, "uT"))
    def test_gridding_sinc(self):
        rf_sinc = cmrseq.bausteine.SincRFPulse.from_shortest(self.system_specs,
                                                             flip_angle=Quantity(90, "degree"),
                                                             time_bandwidth_product=4.)
        rf_sinc2 = cmrseq.bausteine.SincRFPulse.from_shortest(self.system_specs,
                                                              flip_angle=Quantity(180, "degree"),
                                                              time_bandwidth_product=4.,
                                                              delay=Quantity(10, "ms"))

        seq = cmrseq.Sequence([rf_sinc, rf_sinc2], self.system_specs)

        with self.subTest("Dense gridding"):
            t, wf = seq.combined_gradients()

        with self.subTest("Sparse gridding"):
            t, wf = seq.combined_rf()
            fig, ax = plt.subplots(1, 1, constrained_layout=True)
            ax.plot(t, wf.T, "x-")
            fig.savefig(f"{test_plot_output}/sparse_rf_gridding.png")
            plt.close(fig)


class TestADCGridding(unittest.TestCase):
    def test_gridding_adc_only(self):
        """ Test the gridding functionality in case the ADC is the only block"""

        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"),
                                         adc_raster_time=Quantity(0.01, "ms"))
        adc = cmrseq.bausteine.SymmetricADC(system_specs=system_specs,
                                            num_samples=10,
                                            duration=Quantity(2, 'ms'), delay=Quantity(0, 'ms'))
        seq = cmrseq.Sequence([adc], system_specs=system_specs)
        t, adc_on, adc_phase, start_end = seq.adc_to_grid(force_raster=False)
        self.assertEqual(int(np.sum(adc_on)), adc._n_samples)

    def test_gridding_adc_latest(self):
        """ Test the gridding functionality in case the ADC block extends to longer times than
        any other Sequence block"""
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"),
                                         adc_raster_time=Quantity(0.01, "ms"))
        delay = cmrseq.bausteine.Delay(system_specs=system_specs, duration=Quantity(0.1, 'ms'))
        adc = cmrseq.bausteine.SymmetricADC(system_specs=system_specs, num_samples=10,
                                            duration=Quantity(2, 'ms'), delay=Quantity(0, 'ms'))
        seq = cmrseq.Sequence([delay], system_specs=system_specs)
        seq.append(adc)
        seq.append(delay, copy=True)

        t, adc_on, adc_phase, start_end = seq.adc_to_grid(force_raster=False)
        self.assertEqual(int(np.sum(adc_on)), adc._n_samples)
        self.assertEqual(t[0], 0)
        self.assertEqual(t[-1], Quantity(2.2, "ms").m)

    def test_gridding_symmetric_adc_with_gradient(self):
        """ Test """
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"),
                                         adc_raster_time=Quantity(0.01, "ms"))

        f, axes = plt.subplots(2, 1, figsize=(10, 6))

        def _plot(tuni, startend_uni, tnonuni, startend_nonuni, wf, a):

            a.plot(wf[0], wf[1]/np.max(wf[1]), alpha=0.5)
            a.axvline(tuni[0, startend_uni[0, 1]], alpha=0.3, linestyle="--", linewidth=2, color="C1")
            a.axvline(tuni[0, startend_uni[0, 0]], alpha=0.3, linestyle="--", linewidth=2, color="C1")
            a.axvline(tnonuni[0, startend_nonuni[0, 1]], alpha=0.5, linestyle="--", linewidth=2, color="C2")
            a.axvline(tnonuni[0, startend_nonuni[0, 0]], alpha=0.5, linestyle="--", linewidth=2, color="C2")

            a.plot(tuni[0], tuni[1], "x", markersize=8, label="force_gradient_raster=True")
            a.plot(tnonuni[0], tnonuni[1], "+", markersize=8, label="force_gradient_raster=False")
            a.grid(True), a.set_ylim([-0.1, 1.4]),
            a.set_xlim([tuni[0, 0]-0.5, tuni[0, -1]+0.5])
            a.legend()

            a.text(tuni[0, startend_uni[0, 0]], 1.2, "Uniform Start", color="C1")
            a.text(tuni[0, startend_uni[0, 1]], 1.2, "Uniform End", color="C1")
            a.text(tnonuni[0, startend_nonuni[0, 0]], 1.1, "Non-Uniform Start", color="C2")
            a.text(tnonuni[0, startend_nonuni[0, 1]], 1.1, "Non-Uniform End", color="C2")

        sequence_even = cmrseq.seqdefs.readout.gre_cartesian_line(system_specs, num_samples=20,
                                                                  k_readout=Quantity(10.,'1/m'),
                                                                  k_phase=Quantity(10.,'1/m'),
                                                                  adc_duration=Quantity(4.,'ms'))
        tg, wf = sequence_even.gradients_to_grid()
        wf = np.concatenate([tg[np.newaxis], wf], axis=0)

        tuni, activation_uni, _, startend_uni = sequence_even.adc_to_grid(force_raster=True)
        tuni = np.stack([tuni, activation_uni])
        tnonuni, activation_nonuni, _, startend_nonuni = sequence_even.adc_to_grid(force_raster=False)
        tnonuni = np.stack([tnonuni, activation_nonuni])
        _plot(tuni, startend_uni, tnonuni, startend_nonuni, wf, axes[0])
        axes[0].set_title("Even Number of Samples (20)")

        sequence_odd = cmrseq.seqdefs.readout.gre_cartesian_line(system_specs, num_samples=21,
                                                                  k_readout=Quantity(10.,'1/m'),
                                                                  k_phase=Quantity(10.,'1/m'),
                                                                  adc_duration=Quantity(4.,'ms'))
        tg, wf = sequence_odd.gradients_to_grid()
        wf = np.concatenate([tg[np.newaxis], wf], axis=0)
        tuni, activation_uni, _, startend_uni = sequence_odd.adc_to_grid(force_raster=True)
        tuni = np.stack([tuni, activation_uni])
        tnonuni, activation_nonuni, _, startend_nonuni = sequence_odd.adc_to_grid(force_raster=False)
        tnonuni = np.stack([tnonuni, activation_nonuni])
        _plot(tuni, startend_uni, tnonuni, startend_nonuni, wf, axes[1])
        axes[1].set_title("Odd Number of Samples (21)")
        f.tight_layout()
        f.suptitle("ADC To grid w & w/o force to raster")
        f.savefig(f"{test_plot_output}/adc_to_grid.svg")
        plt.close(f)

class TestSequenceTransformations(unittest.TestCase):
    """ Tests covering the transformation forwarding to contained blocks"""

    def test_time_reverse(self):
        system_specs1 = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                          max_slew=Quantity(200., "mT/m/ms"),
                                          grad_raster_time=Quantity(0.01, "ms"),
                                          rf_raster_time=Quantity(0.01, "ms"))
        l1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=system_specs1,
                                                               orientation=np.array([1., 0., 0.]),
                                                               amplitude=Quantity(20, "mT/m"),
                                                               duration=Quantity(1., "ms"))
        seq1 = cmrseq.Sequence([l1], system_specs1)
        seq11 = seq1.copy()
        seq11.time_reverse()
        t1, gwf1 = seq1.combined_gradients()
        t2, gwf2 = seq11.combined_gradients()
        self.assertTrue(np.allclose(gwf1, gwf2))

class TestSequenceValidation(unittest.TestCase):

    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              adc_raster_time=Quantity(0.001, "ms"),
                                              grad_raster_time=Quantity(0.01, "ms"),
                                              rf_raster_time=Quantity(0.01, "ms"),
                                              adc_dead_time=Quantity(50, "us"),
                                              rf_dead_time=Quantity(100, "us"),
                                              rf_ringdown_time=Quantity(120, "us")
                                              )
    def test_overlapping_grad(self):
        with self.subTest("Combined exceeding max grad"):
            max_grad = cmrseq.bausteine.TrapezoidalGradient(self.system_specs,
                                                            orientation=np.array([1., 0., 0.]),
                                                            amplitude=self.system_specs.max_grad,
                                                            flat_duration=Quantity(500, "us"),
                                                            rise_time=self.system_specs.minmax_risetime)
            max_grad_copy = max_grad.copy()

            with self.assertRaises(ValueError, msg="Sequence does not raise Value error for a combined"
                                                   "Gradient exceeding system limits") as cm:
                _ = cmrseq.Sequence([max_grad, max_grad_copy], self.system_specs)

        with self.subTest("Combined exceeding max slew"):
            max_slew_grad = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
                                                            self.system_specs,
                                                            orientation=np.array([1., 0., 0.]),
                                                            amplitude=self.system_specs.max_grad/3,
                                                            flat_duration=Quantity(500, "us"))
            max_slew_grad_copy = max_grad.copy()
            with self.assertRaises(ValueError, msg="Sequence does not raise Value error for a combined"
                                                   "Gradient exceeding system limits") as cm:
                _ = cmrseq.Sequence([max_slew_grad, max_slew_grad_copy], self.system_specs)



    def test_overlapping_adc(self):
        adc0 = cmrseq.bausteine.SymmetricADC(self.system_specs, num_samples=100,
                                             duration=Quantity(1, "ms"))
        adc1 = cmrseq.bausteine.SymmetricADC(self.system_specs, num_samples=100,
                                             duration=Quantity(1, "ms"),
                                             delay=adc0.tmax/2)
        adc2 = cmrseq.bausteine.SymmetricADC(self.system_specs, num_samples=100,
                                             duration=Quantity(1, "ms"),
                                             delay=adc0.tmax)
        adc3 = cmrseq.bausteine.SymmetricADC(self.system_specs, num_samples=100,
                                             duration=Quantity(1, "ms"),
                                             delay=adc0.tmax + self.system_specs.adc_dead_time)

        msg = "Sequence does not raise Value error in validation for overlapping sampling events"
        with self.assertRaises(ValueError, msg=msg) as cm:
            _ = cmrseq.Sequence([adc0, adc1], self.system_specs)

        msg = ("Sequence does not raise Value error in validation for non overlapping events"
               "with violating dead-time")
        with self.assertRaises(ValueError, msg=msg) as cm:
            _ = cmrseq.Sequence([adc0, adc2], self.system_specs)

        # should not fail
        _ = cmrseq.Sequence([adc0, adc3], self.system_specs)

    def test_overlapping_rf(self):
        rf0 = cmrseq.bausteine.SincRFPulse(system_specs=self.system_specs,
                                           flip_angle=Quantity(np.pi / 2, "rad"),
                                           duration=Quantity(1., "ms"),
                                           center=0.5,
                                           delay=Quantity(0., "ms"),
                                           apodization=0.)
        rf1 = rf0.copy()
        rf1.shift(rf0.tmax / 2)

        rf2 = rf0.copy()
        rf2.shift(rf0.tmax)

        rf3 = rf0.copy()
        rf3.shift(rf0.tmax+self.system_specs.rf_dead_time)

        msg = "Sequence does not raise Value error in validation for overlapping rf events"
        with self.assertRaises(ValueError, msg=msg) as cm:
            _ = cmrseq.Sequence([rf0, rf1], self.system_specs)

        msg = ("Sequence does not raise Value error in validation for non-overlapping rf events"
               "with violating dead time")
        with self.assertRaises(ValueError, msg=msg) as cm:
            _ = cmrseq.Sequence([rf0, rf2], self.system_specs)

        # Should not fail
        _ = cmrseq.Sequence([rf0, rf3], self.system_specs)

    def test_rf_ringdown(self):
        adc0 = cmrseq.bausteine.SymmetricADC(self.system_specs,
                                             num_samples=100,
                                             duration=Quantity(0.5, "ms"))
        rf0 = cmrseq.bausteine.SincRFPulse(system_specs=self.system_specs,
                                            flip_angle=Quantity(np.pi/2, "rad"),
                                            duration=Quantity(1., "ms"),
                                            center=0.5,
                                            delay=Quantity(0., "ms"),
                                            apodization=0.)

        with self.subTest("ADC starts during RF"):
            with self.assertRaises(ValueError) as _:
                seq = cmrseq.Sequence([rf0, adc0], self.system_specs)


        with self.subTest("ADC starts during ring down"):
            with self.assertRaises(ValueError) as _:
                adc1 = adc0.copy()
                adc1.shift(-adc0.tmin + rf0.tmax)
                seq = cmrseq.Sequence([rf0, adc1], self.system_specs)

        with self.subTest("Second RF starts before ADC is finished"):
            with self.assertRaises(ValueError) as _:
                adc1 = adc0.copy()
                adc1.shift(-adc0.tmin + rf0.tmax + self.system_specs.rf_ringdown_time)
                rf1 = rf0.copy()
                rf1.shift(adc1.tmax - Quantity(100, "us"))
                seq = cmrseq.Sequence([rf0, adc1, rf1], self.system_specs)

        with self.subTest("Consecutive RF, followed by violating ADC"):
            with self.assertRaises(ValueError) as _:
                rf1 = rf0.copy()
                rf1.shift(rf0.tmax + self.system_specs.rf_dead_time)
                adc1 = adc0.copy()
                adc1.shift(-adc0.tmin + rf0.tmax)
                seq = cmrseq.Sequence([rf0, rf1, adc1], self.system_specs)

        with self.subTest("Consecutive ADC, followed by violating RF"):
            with self.assertRaises(ValueError) as _:
                adc1 = adc0.copy()
                adc1.shift(-adc0.tmin + adc0.tmax + self.system_specs.adc_dead_time)
                rf1 = rf0.copy()
                rf1.shift(-rf1.tmin + adc1.tmax - Quantity(100, "us"))
                seq = cmrseq.Sequence([adc0, adc1, rf1], self.system_specs)

        with self.subTest("RF / ADC Only"):
            seq = cmrseq.Sequence([adc0], self.system_specs)
            seq = cmrseq.Sequence([rf0], self.system_specs)

class TestAppend(unittest.TestCase):

    def setUp(self) -> None:
        self.system_specs0 = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                               max_slew=Quantity(120., "mT/m/ms"),
                                               adc_raster_time=Quantity(0.001, "ms"),
                                               grad_raster_time=Quantity(0.01, "ms"),
                                               rf_raster_time=Quantity(0.01, "ms"),
                                               adc_dead_time=Quantity(0, "us"),
                                               rf_dead_time=Quantity(0, "us"),
                                               rf_lead_time=Quantity(0., "us"),
                                               rf_ringdown_time=Quantity(0, "us"),
                                               enable_simulatenous_trasmit_receive=True
                                               )
        self.system_specs1 = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                               max_slew=Quantity(120., "mT/m/ms"),
                                               adc_raster_time=Quantity(0.001, "ms"),
                                               grad_raster_time=Quantity(0.01, "ms"),
                                               rf_raster_time=Quantity(0.01, "ms"),
                                               adc_dead_time=Quantity(50, "us"),
                                               rf_dead_time=Quantity(100, "us"),
                                               rf_ringdown_time=Quantity(400, "us"),
                                               rf_lead_time=Quantity(200., "us"),
                                               enable_simulatenous_trasmit_receive = True
                                               )
        self.system_specs2 = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                               max_slew=Quantity(120., "mT/m/ms"),
                                               adc_raster_time=Quantity(0.001, "ms"),
                                               grad_raster_time=Quantity(0.01, "ms"),
                                               rf_raster_time=Quantity(0.01, "ms"),
                                               adc_dead_time=Quantity(400, "us"),
                                               rf_dead_time=Quantity(100, "us"),
                                               rf_ringdown_time=Quantity(50, "us"),
                                               enable_simulatenous_trasmit_receive = True
                                               )
        self.adc = cmrseq.bausteine.SymmetricADC(self.system_specs0,
                                                 num_samples=100,
                                                 duration=Quantity(0.5, "ms"))
        self.rf = cmrseq.bausteine.SincRFPulse(system_specs=self.system_specs0,
                                               flip_angle=Quantity(np.pi / 2, "rad"),
                                               duration=Quantity(0.5, "ms"),
                                               center=0.5,
                                               delay=Quantity(0., "ms"),
                                               apodization=0.)
        self.grad = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
            self.system_specs0,
            np.array([1., 2, 3]),
            flat_duration=Quantity(1, "ms"),
            amplitude=Quantity(10, "mT/m"))
    def test_append_single_block(self):
        with self.subTest("Append ADC to RF - No ringdown, no adc-delay"):
            seq = cmrseq.Sequence([self.rf], self.system_specs0)
            self.assertEqual(seq._get_append_delay(self.adc), seq.end_time)

        with self.subTest("Append ADC to RF - No ringdown with adc-delay"):
            seq = cmrseq.Sequence([self.rf], self.system_specs0)
            adc_tmp = self.adc.copy()
            adc_tmp.shift(Quantity(1, "ms"))
            self.assertEqual(seq._get_append_delay(adc_tmp), seq.end_time)

        with self.subTest("Append ADC to [RF, ADC] - Ring down > ADC deadtime"):
            # As concurrent RF and ADC is allowed here, adc_deadtime still is the
            # limiting factor
            seq = cmrseq.Sequence([self.adc, self.rf], self.system_specs1)
            self.assertEqual(seq._get_append_delay(self.adc),
                             seq.end_time + self.system_specs1.adc_dead_time)

            # Now disable concurrent
            tmp_syst = self.system_specs1.modified_copy(enable_simulatenous_trasmit_receive=False)
            seq = cmrseq.Sequence([self.rf], tmp_syst)
            self.assertEqual(seq._get_append_delay(self.adc),
                             seq.end_time + tmp_syst.rf_ringdown_time)

            seq.append(self.adc)
            fig = cmrseq.plotting.plot_sequence(seq, axes="single", add_legend=False)
            cmrseq.plotting.anotate_timing(seq[0].tmax, seq[-1].tmin, ypos=-10, axis=fig.axes[1],
                                           text=f"Ringdown\n{self.system_specs1.rf_ringdown_time}")
            fig.savefig(f"{test_plot_output}/ring_down.svg")

        with self.subTest("Append ADC to [RF, ADC] - Ring down < ADC deadtime"):
            seq = cmrseq.Sequence([self.adc, self.rf], self.system_specs2)
            self.assertEqual(seq._get_append_delay(self.adc),
                             seq.end_time + self.system_specs2.adc_dead_time)

            seq.append(self.adc)
            fig = cmrseq.plotting.plot_sequence(seq, axes="single", add_legend=False)
            cmrseq.plotting.anotate_timing(seq[1].tmax, seq[-1].tmin, ypos=-10, axis=fig.axes[1],
                                           text=f"ADC dead\n{self.system_specs2.adc_dead_time}")
            fig.savefig(f"{test_plot_output}/adc_dead.svg")

        with self.subTest("Append RF to RF"):
            seq = cmrseq.Sequence([self.rf], self.system_specs1)
            self.assertEqual(seq._get_append_delay(self.rf),
                             seq.end_time + self.system_specs2.rf_dead_time)

            seq.append(self.rf)
            fig = cmrseq.plotting.plot_sequence(seq, axes="single", add_legend=False)
            cmrseq.plotting.anotate_timing(seq[0].tmax, seq[1].tmin, ypos=-10, axis=fig.axes[1],
                                           text=f"RF dead\n{self.system_specs2.rf_dead_time}")
            fig.savefig(f"{test_plot_output}/rf_dead.svg")

        with self.subTest("Append RF to ADC"):
            seq = cmrseq.Sequence([self.adc], self.system_specs1)
            self.assertEqual(seq._get_append_delay(self.rf),
                             seq.end_time + self.system_specs1.rf_lead_time)

        with self.subTest("Append Grad"):
            seq = cmrseq.Sequence([self.adc], self.system_specs1)
            self.assertEqual(seq._get_append_delay(self.grad), seq.end_time)
            seq = cmrseq.Sequence([self.rf], self.system_specs1)
            self.assertEqual(seq._get_append_delay(self.grad), seq.end_time)
            seq = cmrseq.Sequence([self.grad], self.system_specs1)
            self.assertEqual(seq._get_append_delay(self.grad), seq.end_time)

    def test_append_sequence(self):
        with self.subTest("Append ADC to RF - No ringdown, no adc-delay"):
            seq = cmrseq.Sequence([self.rf], self.system_specs0)
            tmp_seq = cmrseq.Sequence([self.adc], self.system_specs0)
            self.assertEqual(seq._get_append_delay(tmp_seq), seq.end_time)

        with self.subTest("Append ADC to RF - No ringdown with adc-delay"):
            seq = cmrseq.Sequence([self.rf], self.system_specs0)
            adc_tmp = self.adc.copy()
            adc_tmp.shift(Quantity(1, "ms"))
            tmp_seq = cmrseq.Sequence([adc_tmp], self.system_specs0)
            self.assertEqual(seq._get_append_delay(tmp_seq), seq.end_time)

        with self.subTest("Append ADC to [RF, ADC] - Ring down > ADC deadtime"):
            # As concurrent RF and ADC is allowed here, adc_deadtime still is the
            # limiting factor
            seq = cmrseq.Sequence([self.adc, self.rf], self.system_specs1)
            tmp_seq = cmrseq.Sequence([self.adc], self.system_specs0)
            self.assertEqual(seq._get_append_delay(tmp_seq),
                             seq.end_time + self.system_specs1.adc_dead_time)

        with self.subTest("Append RF to RF"):
            seq = cmrseq.Sequence([self.rf], self.system_specs1)
            tmp_seq = cmrseq.Sequence([self.rf], self.system_specs0)
            self.assertEqual(seq._get_append_delay(tmp_seq),
                             seq.end_time + self.system_specs2.rf_dead_time)

        with self.subTest("Append RF to ADC"):
            seq = cmrseq.Sequence([self.adc], self.system_specs1)
            tmp_seq = cmrseq.Sequence([self.rf], self.system_specs1)
            self.assertEqual(seq._get_append_delay(tmp_seq), seq.end_time +
                             self.system_specs1.rf_lead_time)

    def test_extend(self):
        seq = cmrseq.Sequence([], self.system_specs0)
        seq.extend([self.rf, self.rf, self.adc, self.adc, self.rf, self.grad])
        fig = cmrseq.plotting.plot_sequence(seq, axes="single", add_legend=False)
        fig.savefig(f"{test_plot_output}/sequence_extend.svg")

        seq.extend([seq, seq], copy=True)
        fig = cmrseq.plotting.plot_sequence(seq, axes="single", add_legend=False)
        fig.savefig(f"{test_plot_output}/sequence_extend_twice.svg")


    def test_append_logic(self):
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"),
                                         adc_raster_time=Quantity(0.01, "ms"),
                                         )
        l1 = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=system_specs,
                                                               orientation=np.array([1., 0., 0.]),
                                                               amplitude=Quantity(20, "mT/m"),
                                                               duration=Quantity(1., "ms"))

        seq1 = cmrseq.Sequence([l1], system_specs)

        with self.subTest("Append with copy"):
            dur_pre = seq1.duration
            seq1.append(seq1, copy=True)
            self.assertEqual(dur_pre*2, seq1.duration)

        with self.subTest("Incompatible add"):
            # Define a valid trapezoid with a duration incompatible to the first systemspec
            lerr = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(
                system_specs=cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                               max_slew=Quantity(200., "mT/m/ms"),
                                               grad_raster_time=Quantity(0.005, "ms"),
                                               adc_raster_time=Quantity(0.001, "ms"),
                                               rf_raster_time=Quantity(0.005, "ms")),
                orientation=-np.array([1., 0., 0.]),
                amplitude=Quantity(20, "mT/m"),
                duration=Quantity(1.005, "ms"))
            self.assertRaises(ValueError, lambda: seq1.append(lerr))

        with self.subTest("Add blocks to empty Sequence"):
            seq_empty = cmrseq.Sequence([], system_specs)
            seq_empty.append(seq1, copy=True)
            self.assertEqual(seq_empty.duration, seq1.duration)

        with self.subTest("Invalid append type"):
            seq_dum = deepcopy(seq1)
            self.assertRaises(NotImplementedError, lambda : seq_dum.append(1))

class TestSequenceUtil(unittest.TestCase):

    def test_get_attribute(self):
        system_specs1 = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                          max_slew=Quantity(200., "mT/m/ms"),
                                          grad_raster_time=Quantity(0.01, "ms"),
                                          rf_raster_time=Quantity(0.01, "ms"))

        blocks = [cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=system_specs1,
                                                  orientation=np.array([1., 0., 0.]),
                                                  amplitude=Quantity(20, "mT/m"),
                                                  duration=Quantity(1., "ms"),
                                                  delay=Quantity(i, "ms"), name="trap")
                  for i in (0, 1.3, 2.3, 4)]
        blocks.extend([cmrseq.bausteine.SincRFPulse(system_specs1, duration=Quantity(2, "ms"),
                                                    delay=Quantity(delay, "ms"))
                       for delay in [0., 2.1]])
        seq1 = cmrseq.Sequence(blocks, system_specs1)

        self.assertTrue(np.isclose(seq1["trap_0"].tmin.m_as("ms"), 0, atol=1e-4))
        self.assertTrue(np.isclose(seq1[0].tmin.m_as("ms"), 0, atol=1e-4))
        self.assertTrue(len([b.name for b in seq1]) == len(blocks))
        self.assertTrue(len([b.name for b in seq1[0:3]]) == 3)
        self.assertTrue(len([b.name for b in seq1[(0, 1, 2)]]) == 3)

        self.assertTrue(len(seq1.get_block(partial_string_match="si")) == 2)
        self.assertTrue(len(seq1.get_block(regular_expression=".*si.*")) == 2)
        self.assertTrue(np.isclose(seq1.get_block('trap_0').tmin.m_as("ms"), 0, atol=1e-4))

    def test_calc_kspace(self):
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"))

        lphase = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                      orientation=np.array([0., 1., 0.]),
                                                      amplitude=Quantity(10, "mT/m"),
                                                      flat_duration=Quantity(2.8, "ms"),
                                                      rise_time=Quantity(0.1, "ms"),
                                                      delay=Quantity(1.02, "ms"))

        l1 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                  orientation=np.array([-1., 0., 0.]),
                                                  amplitude=Quantity(10, "mT/m"),
                                                  flat_duration=Quantity(2.8, "ms"),
                                                  rise_time=Quantity(0.1, "ms"),
                                                  delay=Quantity(1.02, "ms"))

        l2 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                  orientation=np.array([1., 0., 0.]),
                                                  amplitude=Quantity(10, "mT/m"),
                                                  flat_duration=Quantity(5.6, "ms"),
                                                  rise_time=Quantity(0.1, "ms"),
                                                  delay=Quantity(l1.gradients[0][-1], "ms"))

        rf_sinc = cmrseq.bausteine.SincRFPulse(system_specs=system_specs,
                                               flip_angle=Quantity(np.pi/2, "rad"),
                                               duration=Quantity(1., "ms"),
                                               center=0.5,
                                               delay=Quantity(0.01, "ms"),
                                               apodization=0.)
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(
                                            system_specs=system_specs, num_samples=101,
                                            duration=Quantity(5.6, "ms"), delay=l2.gradients[0][1])

        seq = cmrseq.Sequence([l1, l2, lphase, rf_sinc, adc], system_specs=system_specs)
        f, (a, ak) = plt.subplots(1, 2, figsize=(13, 4))
        cmrseq.plotting.plot_sequence(seq, axes=a, adc_yoffset=12.5)
        cmrseq.plotting.plot_kspace_2d(seq, k_axes=(0, 1), ax=ak)
        f.suptitle("Calculate k-space")
        f.savefig(f"{test_plot_output}/k_space.svg")

    def test_calculate_moment(self):
        orientation = np.array([1., 0., 0.])
        area = Quantity(20, "mT/m*ms")
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"))
        l1 = cmrseq.bausteine.TrapezoidalGradient.from_area(
                                        system_specs=system_specs,
                                        orientation=orientation, area=area)
        seq1 = cmrseq.Sequence([l1], system_specs)

        with self.subTest("Without end time"):
            m0 = seq1.calculate_moment(0)
            self.assertTrue(np.allclose(m0, area * orientation))

        with self.subTest("With specified end time"):
            m0 = seq1.calculate_moment(0, end_time=seq1.end_time)
            self.assertTrue(np.allclose(m0, area * orientation))

        with self.subTest("Call on empty sequence"):
            dummyseq = cmrseq.Sequence([], system_specs)
            m0 = dummyseq.calculate_moment(0)
            print(m0)
            self.assertTrue(np.allclose(m0, area * orientation * 0.))

    def test_plot_blocknames(self):
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                         max_slew=Quantity(200., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"))

        lphase = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                      orientation=np.array([0., 1., 0.]),
                                                      amplitude=Quantity(10, "mT/m"),
                                                      flat_duration=Quantity(2.8, "ms"),
                                                      rise_time=Quantity(0.1, "ms"),
                                                      delay=Quantity(1.02, "ms"))

        l1 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                  orientation=np.array([-1., 0., 0.]),
                                                  amplitude=Quantity(10, "mT/m"),
                                                  flat_duration=Quantity(2.8, "ms"),
                                                  rise_time=Quantity(0.1, "ms"),
                                                  delay=Quantity(1.02, "ms"))

        l2 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                  orientation=np.array([1., 0., 0.]),
                                                  amplitude=Quantity(10, "mT/m"),
                                                  flat_duration=Quantity(5.6, "ms"),
                                                  rise_time=Quantity(0.1, "ms"),
                                                  delay=Quantity(l1.gradients[0][-1], "ms"))

        rf_sinc = cmrseq.bausteine.SincRFPulse(system_specs=system_specs,
                                               flip_angle=Quantity(np.pi/2, "rad"),
                                               duration=Quantity(1., "ms"),
                                               center=0.5,
                                               delay=Quantity(0.01, "ms"),
                                               apodization=0.)
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(
                                            system_specs=system_specs, num_samples=101,
                                            duration=Quantity(5.6, "ms"), delay=l2.gradients[0][1])

        seq = cmrseq.Sequence([l1, l2, lphase, rf_sinc, adc], system_specs=system_specs)
        f, a = plt.subplots(1, 1, figsize=(13, 4))
        cmrseq.plotting.plot_block_names(seq, axis=a)
        f.suptitle("Sequence block names")
        f.savefig(f"{test_plot_output}/block_names.svg")