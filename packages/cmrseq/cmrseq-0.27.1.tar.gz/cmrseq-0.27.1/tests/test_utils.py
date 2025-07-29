import unittest
import os

import numpy as np
from pint import Quantity

import cmrseq

test_plot_output = f"{os.path.dirname(__file__)}/output/utils/"
os.makedirs(test_plot_output, exist_ok=True)

class CoordinatesTest(unittest.TestCase):
    def test_mps_xyz(self):
        ro_dir = np.array([1., 1., 0])
        ss_dir = np.array([0., 0., 1])
        test_dir_mps = np.array([1., 0., 0.]).reshape(1, 3)
        test_dir_xyz = cmrseq.utils.mps_to_xyz(test_dir_mps, ss_dir, ro_dir)
        self.assertTrue(np.allclose(np.array([1., -1., 0]), test_dir_xyz * np.sqrt(2)),
                        msg="transformed test direction not as expected")
        self.assertTrue(np.isclose(np.linalg.norm(test_dir_mps), np.linalg.norm(test_dir_xyz)),
                        msg="Norm of transformed test direction changed")

        back_transformed = cmrseq.utils.xyz_to_mps(test_dir_xyz, ss_dir, ro_dir)
        self.assertTrue(np.allclose(back_transformed, test_dir_mps),
                        msg="consecutive back/forward transformation yielded differing result")




class TestReport(unittest.TestCase):
    def test_generate_report(self) -> None:
        system_specs = cmrseq.SystemSpec(max_grad=Quantity(40, "mT/m"),
                                              max_slew=Quantity(120., "mT/m/ms"),
                                              grad_raster_time=Quantity(0.001, "ms"),
                                              rf_raster_time=Quantity(0.001, "ms"))

        echo_time = Quantity(1, "ms")
        repetition_time = Quantity(6., "ms")
        matrix_size = np.array([11, 11])
        inplane_resolution = Quantity([1, 1], "mm")
        slice_thickness = Quantity(10, "mm")
        adc_duration = Quantity(2.5, "ms")
        pulse_duration = Quantity(1.5, "ms")
        flip_angle = Quantity(np.pi / 4, "rad")

        seq_list = cmrseq.seqdefs.sequences.flash(system_specs=system_specs,
                                                  matrix_size=matrix_size,
                                                  inplane_resolution=inplane_resolution,
                                                  slice_thickness=slice_thickness,
                                                  adc_duration=adc_duration,
                                                  flip_angle=flip_angle,
                                                  pulse_duration=pulse_duration,
                                                  repetition_time=repetition_time,
                                                  echo_time=None,
                                                  slice_position_offset=Quantity(0., "m"),
                                                  time_bandwidth_product=4.,
                                                  fuse_slice_rewind_and_prephaser=True,
                                                  dummy_shots=0 )
        tmp_seq = seq_list[0]
        tmp_seq.extend(seq_list[1:])

        with open(f"{test_plot_output}/report.txt", "w") as f:
            strreport = cmrseq.utils.report(tmp_seq, format="str")
            f.write(strreport)

        with open(f"{test_plot_output}/report.json", "w") as f:
            jsonrep = cmrseq.utils.report(tmp_seq, format="json")
            f.write(jsonrep)

        with open(f"{test_plot_output}/report.html", "w") as f:
            htmlrep = cmrseq.utils.report(tmp_seq, format="html")
            f.write(htmlrep)