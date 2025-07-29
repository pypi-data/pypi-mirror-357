import unittest
import os
import itertools

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt
import math

import cmrseq

test_plot_output = f"{os.path.dirname(__file__)}/output/seqdefs_preparations/"
os.makedirs(test_plot_output, exist_ok=True)


class TestSpinlockPreparation(unittest.TestCase):
    """ Tests for spinlock preparation definitions"""

    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))


    def test_all_spinlocks(self) -> None:
        spin_lock_time = Quantity(50., "ms")
        spin_lock_frequency = Quantity(500., "Hz")
        
        # obtain all defined spin lock preparation functions
        all_spin_lock_preps = [cmrseq.parametric_definitions.preparation.spinlock.__dict__[f] 
                               for f in cmrseq.parametric_definitions.preparation.spinlock.__all__]

        f, axs = plt.subplots(math.ceil(len(all_spin_lock_preps)/2), 2,      # 2 columns, N/2 rows
                              figsize=(12, 2+4*math.ceil(len(all_spin_lock_preps)/2)), 
                              gridspec_kw={"width_ratios":(1, 1)})

        
        for i, spin_lock_function in enumerate(all_spin_lock_preps):
            seq = spin_lock_function(self.system_specs, spin_lock_time, spin_lock_frequency)
            cmrseq.plotting.plot_sequence(seq, axs.flatten()[i], format_axes=True, add_legend=False)
            f.axes[i].set_title(cmrseq.parametric_definitions.preparation.spinlock.__all__[i])
        
        f.suptitle("Spin lock preparations")
        f.tight_layout()
        f.savefig(f"{test_plot_output}/spin_lock_preparations.svg")
        plt.close(f)
