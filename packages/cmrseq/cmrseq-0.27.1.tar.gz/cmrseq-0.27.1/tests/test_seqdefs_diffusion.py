import unittest
import os

from pint import Quantity
import numpy as np
import matplotlib.pyplot as plt

import cmrseq


test_plot_output = f"{os.path.dirname(__file__)}/output/seqdefs_diffusion/"
os.makedirs(test_plot_output, exist_ok=True)

system_specs = cmrseq.SystemSpec(max_grad=Quantity(80, "mT/m"),
                                 max_slew=Quantity(200., "mT/m/ms"),
                                 grad_raster_time=Quantity(0.01, "ms"),
                                 rf_raster_time=Quantity(0.01, "ms"))


class TestDiffusion(unittest.TestCase):
    def test_bipolar(self):
        seq = cmrseq.seqdefs.diffusion.bipolar(system_specs=system_specs,
                                               dt=Quantity(0.5, "ms"),
                                               Dt=Quantity(5, "ms"),
                                               direction=np.array([1., 2., 3.]),
                                               amplitude=Quantity(30., "mT/m"))
        seq_flipped = cmrseq.seqdefs.diffusion.bipolar(system_specs=system_specs,
                                                       dt=Quantity(0.5, "ms"),
                                                       Dt=Quantity(5, "ms"),
                                                       direction=np.array([1., 2., 3.]),
                                                       amplitude=Quantity(30., "mT/m"),
                                                       flip_decoding=True)

        f, (a1, a2) = plt.subplots(2, 1, figsize=(10, 8))
        cmrseq.plotting.plot_sequence(seq, axes=a1)
        cmrseq.plotting.plot_sequence(seq_flipped, axes=a2)
        f.suptitle("Bipolar diffusion 0.5/5 ms at 30 mT/m")
        f.savefig(f"{test_plot_output}/bipolar.svg")
        plt.close(f)

    def test_m012(self):
        with self.subTest("single bvalue"):
            seq = cmrseq.seqdefs.diffusion.m012(system_specs=system_specs,
                                                bvalue=Quantity(430., "s/mm^2"),
                                                zeta=Quantity(0.9, "ms"),
                                                lambda_=Quantity(5.6, "ms"),
                                                direction=np.array([1., 0., 0.]))
            seq_flipped = cmrseq.seqdefs.diffusion.m012(system_specs=system_specs,
                                                        bvalue=Quantity(430., "s/mm^2"),
                                                        zeta=Quantity(0.9, "ms"),
                                                        lambda_=Quantity(5.6, "ms"),
                                                        direction=np.array([1., 0., 0.]),
                                                        flip_decoding=True)
            f, (a1, a2, a3) = plt.subplots(3, 1, figsize=(10, 12))
            cmrseq.plotting.plot_sequence(seq, axes=a1)
            cmrseq.plotting.plot_sequence(seq_flipped, axes=a2)
            cmrseq.plotting.plot_block_names(seq, axis=a3)
            f.suptitle("M012 diffusion"), f.tight_layout()
            f.savefig(f"{test_plot_output}/m012.svg")
            plt.close(f)

        with self.subTest("multiple bvalues"):
            seqlist_unidir = cmrseq.seqdefs.diffusion.m012(system_specs=system_specs,
                                                    bvalue=Quantity([100, 200, 300, 430], "s/mm^2"),
                                                    zeta=Quantity(0.9, "ms"),
                                                    lambda_=Quantity(5.6, "ms"),
                                                    direction=np.array([1., 0., 0.]))

            seqlist_multi_dir = cmrseq.seqdefs.diffusion.m012(system_specs=system_specs,
                                                    bvalue=Quantity([100, 300], "s/mm^2"),
                                                    zeta=Quantity(0.9, "ms"),
                                                    lambda_=Quantity(5.6, "ms"),
                                                    direction=np.array([[1., 0., 0.],
                                                                        [0., 1., 1]]))

            f, a = plt.subplots(2, 1, figsize=(10, 8))
            for seq in seqlist_unidir:
                cmrseq.plotting.plot_sequence(seq, axes=a[0])
            for seq in seqlist_multi_dir:
                cmrseq.plotting.plot_sequence(seq, axes=a[1])
            f.suptitle("M012 diffusion multiple bvalues"), f.tight_layout()
            f.savefig(f"{test_plot_output}/m012_multi_b.svg")
            plt.close(f)

    def test_shortest_m012(self):
        seqlist = cmrseq.seqdefs.diffusion.shortest_m012(system_specs=system_specs,
                                                     bvalues=Quantity([100., 450.], "s/mm^2"),
                                                     direction=np.array([1., 0., 0.]))

        f, a = plt.subplots(1, 1, figsize=(10, 8))
        for seq in seqlist:
            cmrseq.plotting.plot_sequence(seq, axes=a)
        f.suptitle("M012 diffusion shortest"), f.tight_layout()
        f.savefig(f"{test_plot_output}/m012_shortest.svg")
        plt.close(f)