__all__ = ["OMatrix"]

from typing import Tuple, Union

from pint import Quantity
import numpy as np

import cmrseq
from cmrseq.core.bausteine._rf import RFPulse
from cmrseq.core.bausteine._gradients import Gradient
from cmrseq.core.bausteine._gradients import TrapezoidalGradient
from cmrseq.utils._transformations import get_rotation_matrix

from cmrseq._exceptions import BuildingBlockArgumentError

class OMatrix:
    """Captures the transformation of a slice coordinate system (Readout, Phase encoding,
    Slice Normal) to XYZ scanner coordinates.

    When applied to Gradient and corresponding RFPulse objects, a transformed definition of the
    waveforms is returned.

    :raises: BuildingBlockArgumentError if slice_normal and readout_direction are not orthogonal

    :param position: Scalar length value for a positional offset along the slice-normal direction
    :param slice_normal: (3, ) 3D vector containing the slice normal
    :param readout_direction: (3, ) 3D vector containing the readout direction
    :param system_specs:
    """
    #: 4x4 Transformation matrix in homogenous coordinates
    _tmatrix: np.ndarray

    #: (3, )
    _slice_normal: np.ndarray

    #: (3, )
    _readout_dir: np.ndarray

    #: positional_offset in meter
    _position: Quantity

    def __init__(self, position: Quantity, slice_normal: np.ndarray,
                   readout_direction: np.ndarray, system_specs: 'cmrseq.SystemSpec'):

        slice_normal = slice_normal / np.linalg.norm(slice_normal)
        readout_direction = readout_direction / np.linalg.norm(readout_direction)
        self._tmatrix = np.eye(4, 4)
        self._system_specs = system_specs
        self._position = position
        self._readout_dir = readout_direction
        self._slice_normal = slice_normal
        self._update_matrix()

    def _update_matrix(self):
        if not np.isclose(0, np.dot(self._slice_normal, self._readout_dir)):
            raise BuildingBlockArgumentError("Slice normal and readout direction are assumed to"
                                             "be orthogonal but are not",
                                             argument="slice_normal/readout_direction", class_name='OMatrix')
        rot_mat = get_rotation_matrix(self._slice_normal, self._readout_dir,
                                      target_orientation="mps")
        self._tmatrix[:3, :3] = rot_mat
        self._tmatrix[:3, 3] = - self._position.m_as("m")

    def apply(self, block: Union[Gradient, Tuple[RFPulse, TrapezoidalGradient]]) \
             -> Tuple[Quantity, Quantity]:
        """Applies the spatial transformation from Slice-coordinates to XYZ-coordinates to the
        specified block.

        For a Gradient block this means a rotation of the vector defined as the gradient channels
        [gx, gy, gz], where the total gradient area on all channels is preserved.
        The returned values are the time-points (t, ) and transformed gradient-waveform (3, t).

        For a RFPulse the application of the OMatrix only makes sense in presence of a corresponding
        Trapezoidal gradient defining the slice-selective excitation. If given a tuple containing
        (RFPulse, TrapezoidalGradient), the frequency-modulated RF waveform is returned as
        time-points (t, ) and complex-wf (t, ).

        :param block: Either an instance of a Gradient, or a tuple containing an RFPulse as well
            as a corresponding TrapezoidalGradient object defining the slice-selective excitation
        """
        if isinstance(block, Gradient):
            return self._apply_gradient(block)
        elif (isinstance(block, (tuple, list)) and isinstance(block[0], RFPulse) and
              isinstance(block[1], TrapezoidalGradient)):
            return self._apply_rf(block[0], block[1])
        else:
            raise NotImplementedError(f"OMatrices can be applied to either instances of Gradient"
                                      f"or tuples of (RFPulse, TrapezoidalGradient) but received"
                                      f"{block}")

    def _apply_gradient(self, grad: Gradient):
        """Rotates gradients"""
        t, grad = grad.gradients
        grad_transformed = np.einsum('ij, jt -> it', self.tmatrix[:3, :3], grad)
        return Quantity(t, "ms"), Quantity(grad_transformed, "mT/m")

    def _apply_rf(self, rf_block: RFPulse, grad: TrapezoidalGradient):
        """Applied frequency modulation to RF pulse"""
        if not np.isclose((old_freq := rf_block.frequency_offset), Quantity(0, "Hz")):
            raise ValueError(f"Tried to apply orientation matrix to a RFpulse with non-zero "
                             f"frequency offset is not defined: {old_freq}")

        new_freq_offset = (self._system_specs.gamma.to("1/mT/ms") * self._position
                           * grad.magnitude.to("mT/m"))
        rf_block.frequency_offset = new_freq_offset
        t, wf = rf_block.rf
        rf_block.frequency_offset = old_freq
        return Quantity(t, "ms"), Quantity(wf, "uT")

    def update(self, position: Quantity = None, slice_normal: np.ndarray = None,
               readout_direction: np.ndarray = None) -> None:
        """Updates all specified properties of the OMatrix.

        :param position: Scalar length value for a positional offset along the slice-normal direction
        :param slice_normal: (3, ) 3D vector containing the slice normal
        :param readout_direction: (3, ) 3D vector containing the readout direction
        :return:
        """
        if slice_normal is not None:
            self._slice_normal[:] = slice_normal / np.linalg.norm(slice_normal)
        if readout_direction is not None:
            self._readout_dir[:] = readout_direction / np.linalg.norm(readout_direction)
        if position is not None:
            self._position = position.to("m")
        self._update_matrix()

    @property
    def pos_offset(self):
        """Scalar positional offset in 3D"""
        return self._slice_normal * self._position

    @pos_offset.setter
    def pos_offset(self, offset: Quantity):
        """Sets scalar positional offset along slice normal"""
        self._position = offset.to("m")
        self._update_matrix()

    @property
    def tmatrix(self):
        """Returns the (4x4) transformation matrix"""
        read_only_view = self._tmatrix.copy()
        read_only_view.flags.writeable = False
        return read_only_view

    @property
    def slice_normal(self):
        """Return read-only view of the slice-normal"""
        tmp = self._slice_normal.copy()
        tmp.flags.writeable = False
        return tmp

    @slice_normal.setter
    def slice_normal(self, vector: np.ndarray):
        """Updates the slice-normal"""
        self._slice_normal[:] = vector / np.linalg.norm(vector)
        self._update_matrix()

    @property
    def readout_direction(self):
        """Return read-only view of the readout direction"""
        tmp = self._readout_dir.copy()
        tmp.flags.writeable = False
        return tmp

    @readout_direction.setter
    def readout_direction(self, vector: np.ndarray):
        """Updates the readout-direction"""
        self._readout_dir[:] = vector / np.linalg.norm(vector)
        self._update_matrix()
