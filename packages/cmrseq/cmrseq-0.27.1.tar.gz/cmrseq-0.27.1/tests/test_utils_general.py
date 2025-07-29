import unittest
import os

from pint import Quantity
import numpy as np
import matplotlib.pyplot as plt

import cmrseq


test_plot_output = f"{os.path.dirname(__file__)}/output/utils/general/"
os.makedirs(test_plot_output, exist_ok=True)

class TestGeneralUtils(unittest.TestCase):
    def test_concomitant_fields(self):
        seq = cmrseq.contrib.se_m012_ssepi(echo_time=Quantity(90, "ms"),
                                           slice_thickness=Quantity(10, "mm"),
                                           slice_pos_offset=Quantity(0., "mm"),
                                           field_of_view=Quantity([20, 15], "cm"),
                                           matrix_size=np.array([96, 42]),
                                           b_vectors=Quantity(np.eye(3, 3) * 10, "(s/mm^2)^(1/2)"),
                                           )
        seq_ = seq[0].partial_sequence(True,
                                       partial_string_match=["diffusion", "velocity", "rf"])

        f = cmrseq.plotting.plot_sequence(seq_)
        f.savefig(f"{test_plot_output}/sequence.svg")
        coords = np.stack(np.meshgrid(np.linspace(-0.1, 0.1, 25),
                                      np.linspace(-0.15, 0.15, 45),
                                      np.linspace(-0.05, 0.05, 13), indexing="ij"),
                          axis=-1)[..., (1, 0, 2)]
        phase = cmrseq.utils.concomitant_fields(seq_, coords)
        f, ax = plt.subplots(1, 5, constrained_layout=True, figsize=(12, 4))
        for a, dat in zip(ax, phase[:, :, (0, 3, 6, 9, 12)].transpose(2, 0, 1)):
            im = a.imshow(dat, origin="lower")
            plt.colorbar(im, ax=a, location="bottom", orientation="horizontal")
        f.savefig(f"{test_plot_output}/concomitant.svg")

    def test_find_gradient_blocks(self):
        """Constructs a sequence containing a trapezoid, a spiral and a
        combination of two trapezoidals resulting an arbtirary shape
        :return:
        """
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                         max_slew=Quantity(120., "mT/m/ms"),
                                         grad_raster_time=Quantity(0.01, "ms"),
                                         rf_raster_time=Quantity(0.01, "ms"),
                                         adc_raster_time=Quantity(0.01, "ms"))

        b = cmrseq.seqdefs.readout.spiral_pipezwart(system_specs, interleaves=1,
                                                    kr_max = Quantity(40, "1/m"),
                                                    kr_delta = Quantity(10, "1/m"),
                                                    spiral_type = "archimedean",
                                                    gradient_rewind_type = "ramp down",
                                                    undersampling_type = "linear",
                                                    kz_max = Quantity(10, "1/m"),
                                                    kz_delta = Quantity(1, "1/m"))
        c = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([1, 0., 0.]),
                                                 amplitude = Quantity(10, "mT/m"),
                                                 flat_duration = Quantity(1, "ms"),
                                                 rise_time = Quantity(0.2, "ms"))
        d = cmrseq.bausteine.TrapezoidalGradient(system_specs, np.array([0., 1., 0.]),
                                                 amplitude = Quantity(10, "mT/m"),
                                                 flat_duration = Quantity(1, "ms"),
                                                 rise_time = Quantity(0.2, "ms"))
        delay = cmrseq.bausteine.Delay(system_specs, duration=Quantity(0.5, "ms"))
        seq = cmrseq.Sequence([c], system_specs, copy=True)
        seq.append(b, copy=True)
        seq.append(c, copy=True)
        c.shift(Quantity(-0.1, "ms"))
        seq.append(c, copy=True)
        seq.append(delay)
        seq.append(d)
        print(seq.start_time)
        f = cmrseq.plotting.plot_sequence(seq, axes="single")
        f.savefig(f"{test_plot_output}/find_block_input.png")

        t, (gwfx, gwfy, gwfz) = seq.combined_gradients()
        gdefs = cmrseq.utils.find_gradient_blocks(t, gwfx)
        self.assertEqual(len([_ for _ in gdefs if _[0] == "trapezoid"]), 1)
        self.assertEqual(len([_ for _ in gdefs if _[0] == "arbitrary"]), 2)
        gdefs = cmrseq.utils.find_gradient_blocks(t, gwfy)
        self.assertEqual(len([_ for _ in gdefs if _[0] == "trapezoid"]), 1)
        self.assertEqual(len([_ for _ in gdefs if _[0] == "arbitrary"]), 1)
        gdefs = cmrseq.utils.find_gradient_blocks(t, gwfz)
        self.assertEqual(len(gdefs), 0)

    def test_find_gradients(self):
        """Constructs a phase contrast gradient echo, which should result in only trapezoidal
        gradient blocks.
        """
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                         max_slew=Quantity(120., "mT/m/ms"),
                                         grad_raster_time=Quantity(10, "us"),
                                         rf_raster_time=Quantity(1, "us"),
                                         adc_raster_time=Quantity(100, "ns"))
        fov = Quantity([200, 200], "mm")
        matrix_size = np.array((121, 121))
        res = fov / matrix_size
        pulse_duration = Quantity(1.5, "ms")
        adc_duration = Quantity(2, "ms")
        flip_angle = Quantity(np.pi / 6, "rad")
        slice_thickness = Quantity(3, "mm")
        venc_max = Quantity(60, "cm/s")
        venc_direction = np.array([0., 1., 0.])  # in mps

        sequence_list = cmrseq.contrib.pc_gre(system_specs,
                                              matrix_size=matrix_size,
                                              inplane_resolution=res,
                                              slice_thickness=slice_thickness,
                                              adc_duration=adc_duration,
                                              flip_angle=flip_angle,
                                              pulse_duration=pulse_duration,
                                              repetition_time=Quantity(9., "ms"),
                                              echo_time=Quantity(1., "ms"),
                                              venc=venc_max.to("m/s"),
                                              venc_direction=venc_direction,
                                              venc_duration=Quantity(0., "ms"))
        sequence = sequence_list[0].copy()
        sequence.extend(sequence_list[1:])
        t, gwf = sequence.combined_gradients()
        x_blocks = cmrseq.utils.find_gradient_blocks(t, gwf[0])
        y_blocks = cmrseq.utils.find_gradient_blocks(t, gwf[1])
        z_blocks = cmrseq.utils.find_gradient_blocks(t, gwf[2])

        self.assertTrue(len(np.unique([n for (n, t, wf) in x_blocks])) == 1)
        self.assertTrue(np.unique([n for (n, t, wf) in x_blocks])[0] == 'trapezoid')
        self.assertTrue(len(np.unique([n for (n, t, wf) in y_blocks])) == 1)
        self.assertTrue(np.unique([n for (n, t, wf) in y_blocks])[0] == 'trapezoid')
        self.assertTrue(len(np.unique([n for (n, t, wf) in z_blocks])) == 1)
        self.assertTrue(np.unique([n for (n, t, wf) in z_blocks])[0] == 'trapezoid')
