""" cmrseq - A package for defining and modifying Magnetic Resonance Sequences """
__all__ = ["bausteine", "Sequence", "SystemSpec", "seqdefs", "plotting", "utils", "io", "contrib"]
__version__ = "0.27"
from cmrseq.core import bausteine
from cmrseq.core._sequence import Sequence
from cmrseq.core._system import SystemSpec
from cmrseq.core._omatrix import OMatrix
import cmrseq.parametric_definitions as seqdefs

import cmrseq.plotting
import cmrseq.utils
import cmrseq.io
import cmrseq.contrib
import cmrseq._exceptions as err

import warnings
warnings.formatwarning = err.custom_warning_format