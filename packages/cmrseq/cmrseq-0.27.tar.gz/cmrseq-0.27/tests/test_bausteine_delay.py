import unittest
from pint import Quantity

import cmrseq


class TestDelay(unittest.TestCase):
    def setUp(self) -> None:
        self.system_specs = cmrseq.SystemSpec()

    def test_construction(self):
        delay = cmrseq.bausteine.Delay(self.system_specs, duration= Quantity(5., "ms"))
