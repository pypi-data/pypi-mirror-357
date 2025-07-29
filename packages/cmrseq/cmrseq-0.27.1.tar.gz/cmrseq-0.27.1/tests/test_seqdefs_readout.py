import unittest
import os
import itertools

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq

test_plot_output = f"{os.path.dirname(__file__)}/output/seqdefs_readout/"
os.makedirs(test_plot_output, exist_ok=True)


class TestGRECartesian(unittest.TestCase):
    """ Tests for GradientEcho cartesian readout definitions"""

    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              grad_raster_time=Quantity(10, "us"),
                                              rf_raster_time=Quantity(1, "us"),
                                              adc_raster_time=Quantity(100, "ns"))

    def test_cart_line(self):
        k_pe = Quantity(np.arange(-500, 501, 100), "1/m")
        k_ro = Quantity(1 / 0.001, "1/m")
        adc_duration = Quantity(4.05, "ms")
        single_lines = []
        seq_max = cmrseq.seqdefs.readout.gre_cartesian_line(self.system_specs, num_samples=41,
                                                            k_readout=k_ro, k_phase=k_pe[0],
                                                            adc_duration=adc_duration)
        prephaser_duration = seq_max._blocks[0].duration
        for kp in k_pe:
            seq = cmrseq.seqdefs.readout.gre_cartesian_line(self.system_specs, num_samples=41,
                                                            k_readout=k_ro, k_phase=kp,
                                                            adc_duration=adc_duration,
                                                            prephaser_duration=prephaser_duration)
            single_lines.append(seq)

        f, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios":(2, 1)})
        cmrseq.plotting.plot_sequence(single_lines[0], a1, format_axes=True)
        for seq in single_lines[1:]:
            cmrseq.plotting.plot_sequence(seq, [f.axes[2], a1, a1, a1], format_axes=False)
            cmrseq.plotting.plot_kspace_2d(seq, ax=a2)
        f.suptitle("Multi-line cartesian GRE")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/cartesian_gre_line.svg")
        plt.close(f)

    def test_balanced_cart_line(self):
        k_pe = Quantity(np.arange(-500, 501, 100), "1/m")
        k_ro = Quantity(1 / 0.001, "1/m")
        adc_duration = Quantity(5, "ms")
        single_lines = []
        seq_max = cmrseq.seqdefs.readout.balanced_gre_cartesian_line(self.system_specs, num_samples=41,
                                                                     k_readout=k_ro, k_phase=k_pe[0],
                                                                     adc_duration=adc_duration)
        prephaser_duration = seq_max._blocks[0].duration
        for kp in k_pe:
            seq = cmrseq.seqdefs.readout.balanced_gre_cartesian_line(
                                                         self.system_specs, num_samples=41,
                                                         k_readout=k_ro, k_phase=kp, adc_duration=adc_duration,
                                                         prephaser_duration=prephaser_duration)
            single_lines.append(seq)

        f, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios": (2, 1)})
        cmrseq.plotting.plot_sequence(single_lines[0], a1, format_axes=True)
        for seq in single_lines[1:]:
            cmrseq.plotting.plot_sequence(seq, [f.axes[2], a1, a1, a1], format_axes=False)
            cmrseq.plotting.plot_kspace_2d(seq, ax=a2)
        f.suptitle("Multi-line cartesian balanced GRE")
        f.savefig(f"{test_plot_output}/balanced_cartesian_gre_line.svg")
        plt.close(f)


class TestSECartesian(unittest.TestCase):
    """ Tests for SpinEcho cartesian readout definitions"""

    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

    def test_cart_lines(self):
        k_pe = Quantity(np.arange(-500, 501, 100), "1/m")
        k_ro = Quantity(1 / 0.001, "1/m")
        adc_duration = Quantity(5, "ms")
        echo_time = Quantity(15, "ms")
        pulse_duration = Quantity(3, "ms")

        single_lines = []
        seq_max = cmrseq.seqdefs.readout.se_cartesian_line(self.system_specs, num_samples=41,
                                                           echo_time=echo_time,
                                                           pulse_duration=pulse_duration,
                                                           excitation_center_time=pulse_duration/2,
                                                           k_readout=k_ro, k_phase=k_pe[0],
                                                           adc_duration=adc_duration)
        prephaser_duration = self.system_specs.time_to_raster(seq_max["ro_prephaser_0"].duration, "grad")
        print(seq_max["ro_prephaser_0"].duration)

        for kp in k_pe:
            seq = cmrseq.seqdefs.readout.se_cartesian_line(self.system_specs, num_samples=41,
                                                           echo_time=echo_time,
                                                           pulse_duration=pulse_duration,
                                                           excitation_center_time=pulse_duration/2,
                                                           k_readout=k_ro, k_phase=kp,
                                                           adc_duration=adc_duration,
                                                           prephaser_duration=prephaser_duration
                                                           )
            single_lines.append(seq)

        f = plt.figure(constrained_layout=True, figsize=(12, 4))
        axes = f.subplot_mosaic("AAB")

        cmrseq.plotting.plot_sequence(single_lines[0], axes["A"], format_axes=True)
        for seq in single_lines[1:]:
            cmrseq.plotting.plot_sequence(seq, [f.axes[2], axes["A"], axes["A"], axes["A"]],
                                          format_axes=False)
            cmrseq.plotting.plot_kspace_2d(seq, ax=axes["B"])
        f.suptitle("Multi-line cartesian SE")
        f.savefig(f"{test_plot_output}/cartesian_se_line.svg")
        plt.close(f)


class TestEPI(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              grad_raster_time=Quantity(10, "us"),
                                              rf_raster_time=Quantity(1, "us"),
                                              adc_raster_time=Quantity(0.1, "us"))
        
    def test_flat_top_sampling(self):
        fov = Quantity([200, 20], "mm")
        matrix_size = np.array((51, 11))
        partial_fourier_lines = 0

        
        single_shot_epi = cmrseq.seqdefs.readout.single_shot_epi(self.system_specs,
                                                                 field_of_view=fov,
                                                                 matrix_size=matrix_size,
                                                                 blip_direction="up",
                                                                 partial_fourier_lines=partial_fourier_lines,
                                                                 slope_sampling=False,
                                                                 water_fat_shift="minimum")
        fig, ax = plt.subplot_mosaic("AAB;CCB")
        cmrseq.plotting.plot_sequence(single_shot_epi, axes=ax["A"])
        cmrseq.plotting.plot_block_names(single_shot_epi, axis=ax["C"])
        cmrseq.plotting.plot_kspace_2d(single_shot_epi, ax=ax["B"])

        fig.suptitle(f"EPI with slope-sampling")
        fig.set_size_inches(20, 7)
        fig.tight_layout()
        fig.savefig(f"{test_plot_output}/EPI_flat_sampling.png", dpi=100)
        plt.close(fig)

    def test_slope_sampling(self):
        fov = Quantity([200, 20], "mm")
        matrix_size = np.array((51, 11))
        partial_fourier_lines = 0

        single_shot_epi = cmrseq.seqdefs.readout.single_shot_epi(self.system_specs,
                                                                 field_of_view=fov,
                                                                 matrix_size=matrix_size,
                                                                 blip_direction="up",
                                                                 partial_fourier_lines=partial_fourier_lines,
                                                                 slope_sampling=True,
                                                                 water_fat_shift="maximum",
                                                                 max_total_duration=Quantity(30, "ms") 
                                                                 )
        single_shot_epi = cmrseq.seqdefs.readout.single_shot_epi(self.system_specs,
                                                            field_of_view=fov,
                                                            matrix_size=matrix_size,
                                                            blip_direction="up",
                                                            partial_fourier_lines=partial_fourier_lines,
                                                            slope_sampling=True,
                                                            water_fat_shift="minimum",
                                                            max_total_duration=Quantity(30, "ms") 
                                                            )
        fig, ax = plt.subplot_mosaic("AAB;CCB")
        cmrseq.plotting.plot_sequence(single_shot_epi, axes=ax["A"])
        cmrseq.plotting.plot_block_names(single_shot_epi, axis=ax["C"])
        cmrseq.plotting.plot_kspace_2d(single_shot_epi, ax=ax["B"])

        fig.suptitle(f"EPI with flat top-sampling")
        fig.set_size_inches(20, 7)
        fig.tight_layout()
        fig.savefig(f"{test_plot_output}/EPI_slope_sampling.png", dpi=100)
        plt.close(fig)

class TestMultiLineCartesian(unittest.TestCase):
    def setUp(self):
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

    def test_quadratic_fov(self):

        # Define Fourier-Encoding parameters
        fov = Quantity([400, 400], "mm")
        matrix_size = (21, 21)
        res = fov / matrix_size
        adc_duration = Quantity(0.5, "ms")

        sequence_list = cmrseq.seqdefs.readout.multi_line_cartesian(
                                        self.system_specs,
                                        cmrseq.seqdefs.readout.gre_cartesian_line,
                                        matrix_size=matrix_size,
                                        inplane_resolution=res,
                                        adc_duration=adc_duration)
        kspace = np.stack([seq.calculate_kspace()[1] for seq in sequence_list], axis=-1)
        dk = [np.unique(np.round(np.diff(kspace, axis=i), decimals=5)) for i in range(1, 3)]

        print(dk[0][1] / dk[1][1])

        f, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios": (2, 1)})
        cmrseq.plotting.plot_sequence(sequence_list[0], a1, format_axes=True)
        for seq in sequence_list[1:]:
            cmrseq.plotting.plot_sequence(seq, [f.axes[2], a1, a1, a1], format_axes=False)
            cmrseq.plotting.plot_kspace_2d(seq, ax=a2, markersize=20)
        f.suptitle("Multi-line cartesian quadratic FOV")
        f.savefig(f"{test_plot_output}/multi_line_cartesian_gre.svg")
        plt.close(f)


class TestSpiral(unittest.TestCase):
    def test_construction(self):
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                         max_slew=Quantity(120., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.001, "ms"),
                                         rf_raster_time=Quantity(0.001, "ms"))

        undersampling_types = ['linear', 'quadratic', 'hanning']
        spiral_types = ['Archimedean', 'spherical dst']
        gradient_rewinds = [None, "ramp down", "rewind to center"]

        result_blocks = []

        for us, spt, gradrw in itertools.product(undersampling_types, spiral_types, gradient_rewinds):
            with self.subTest(f"spiral with {us}, {spt}, {gradrw}"):
                print(f"spiral with {us}, {spt}, {gradrw}")
                b = cmrseq.seqdefs.readout.spiral_pipezwart(system_specs, interleaves=1,
                                                              kr_max=Quantity(10, "1/m"),
                                                              kr_delta=Quantity(10, "1/m"),
                                                              spiral_type=spt,
                                                              gradient_rewind_type=gradrw,
                                                              undersampling_type=us,
                                                              kz_max=Quantity(10, "1/m"),
                                                              kz_delta=Quantity(1, "1/m"))
                result_blocks.append(b)

        from scipy.integrate import cumulative_trapezoid
        f, axes = plt.subplots(18, 2, figsize=(12, 4*18), gridspec_kw={"width_ratios": (2, 1)})
        for seq, (a1, a2), (us, spt, gradrw) in \
                zip(result_blocks, axes, itertools.product(undersampling_types, spiral_types, gradient_rewinds)):
            t, w = seq.gradients
            ktraj = cumulative_trapezoid(w.m_as("mT/m")[:2], t.m_as("ms"), axis=-1)
            a1.plot(t.m_as("ms"), w.m_as("mT/m").T)
            a2.plot(ktraj[0], ktraj[1])
            a2.spines.left.set_position('zero')
            a2.spines.right.set_color('none')
            a2.spines.bottom.set_position('zero')
            a2.spines.top.set_color('none')
            a2.xaxis.set_ticks_position('bottom')
            a2.yaxis.set_ticks_position('left')
            a2.set_xlim([-0.15, 0.05])
            a2.set_ylim([-0.05, 0.08])
            a1.set_title(f"{us}, {spt}, {gradrw}")
        f.savefig(f"{test_plot_output}/spirals.svg")
        plt.close(f)


