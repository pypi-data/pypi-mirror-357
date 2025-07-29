import unittest
from copy import deepcopy
import os

import numpy as np
from pint import Quantity
import matplotlib.pyplot as plt

import cmrseq


test_plot_output = f"{os.path.dirname(__file__)}/output/systemspecs/"
os.makedirs(test_plot_output, exist_ok=True)


class TestSystemSpecs(unittest.TestCase):
    def test_invalid_raster(self):
        from cmrseq._exceptions import SystemLimitViolationError
        self.assertRaises(SystemLimitViolationError,
                          lambda : cmrseq.SystemSpec(grad_raster_time=Quantity(10, "us"),
                                                     rf_raster_time=Quantity(3, "us"),
                                                     adc_raster_time=Quantity(0.1, "us")))
        valid_specs = cmrseq.SystemSpec(grad_raster_time=Quantity(10, "us"),
                                        rf_raster_time=Quantity(1, "us"),
                                        adc_raster_time=Quantity(0.1, "us"))
        def _tmp():
            valid_specs.adc_raster_time = Quantity(0.3, "us")

        self.assertRaises(SystemLimitViolationError, _tmp)

if __name__ == '__main__':
    unittest.main()
