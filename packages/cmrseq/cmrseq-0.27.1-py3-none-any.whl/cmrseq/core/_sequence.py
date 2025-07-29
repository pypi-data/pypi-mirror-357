""" This Module contains the implementation of the core functionality Sequence"""
__all__ = ["Sequence"]

import collections
from copy import deepcopy
import copy
from typing import List, Union, Iterable, Tuple, Dict, TYPE_CHECKING
from typing import Sequence as typing_Sequence
from warnings import warn
import re

import numpy as np
from pint import Quantity
from tqdm import tqdm

from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core.bausteine._adc import ADC
from cmrseq.core.bausteine._rf import RFPulse
from cmrseq.core.bausteine._gradients import Gradient, TrapezoidalGradient
from cmrseq.core._system import SystemSpec

if TYPE_CHECKING:
    from cmrseq.core._omatrix import OMatrix

class Sequence:
    """ This class serves as a container for MRI-sequence building blocks.

    All blocks contained in a sequence are kept as mutable objects of type SequenceBaseBlock or
    rather its subclasses. This means if a contained block is changed/transformed outside
    the sequence scope, these changes are also reflected in the sequence.

    Below, the functionality provided by a cmrseq.Sequence object is explained according to the
    groups:

    - Instantiation and composition
    - Get contained blocks
    - Gridding, Moments and K-space


    **Instantiation and composition**

    To instantiate a Sequence you need a list containing building blocks and a sytem-specification
    definition. On instantiation, all blocks are validated against the system limits. If any block
    violates the limits, an exception is raised.

    *Adding blocks*: Blocks or even entire sequences can be added to an existing sequence object
    one the obe hand by using the :code:'add_block', :code:'append', :code:'extend' methods
    (see documentation). And on the other hand, the Sequence class implements the addition operator,
    which combines two sequence objects into either a new object containing copies of all blocks
    contained in the other two or by in-place addition where no copies are made:

    .. code::

        new_sequence_object = sequence1 + sequence2   # Combination with copy
        sequence1 += sequence2                        # inplace combination of seq2 into seq1


    *Unique names*: a sequence objects keeps a mapping of automatically created unique names to the
    actual blocks. Whenever blocks are added

    **Get contained blocks**

    There are multiple ways to query single or even multiple blocks at once from the sequence
    object. To get a complete list of unique block-names use the property :code:`seq.blocks`.

    *Access by name*:
    1. Indexing by unique name: :code:`seq["trapezoidal_0"]`
    2. Get all blocks by partial string match: :code:`seq.get_block(partial_string_match=...)`
    3. Get all blocks by matching regular expression on unique names:
        :code:`seq.get_block(regular_expression=...)`
    4. Get a sequence object containing copies of all blocks matched as in (2. & 3.)
        :code:`seq.partial_sequence(...)`

    *Assuming temporal order of start*
    1. Indexing by integer: :code:`seq[0]`
    2. Indexing by slice: :code:`seq[0:5]`
    3. Indexing by tuple of integers: :code:`seq[(0, 2, 5)]`
    4. Iterating over sequence: :code:`[block for block in seq]`
    5. Iterating over sequence with block-names
        :code:`{name: block for (name, block) in seq.items()}`


    **Gridding, Moments and K-space**

    Gradients, RF and ADCs represented on a dense temporal grid defined by the system raster times
    can be obtained by calling the methods: :code:`gradients_to_grid`,
    :code:`rf_to_grid`, and :code:`adc_to_grid`.

    Gradient moments of specified order can be integrated using the function
     :code:`seq.calculate_moment`.

    To get a representation of the kspace-trajectory as well as timing and position of sampling
    events defined by contained ADC blocks can be obtained by the :code:`seq.calculate_kspace`
     function.

    :param building_blocks: List of building Blocks
    :param system_specs: Instance of SystemSpec
    :param snap_to_raster:
    :param copy:
    """
    #: Orientation Matrices - Dict(np.array, List[str]) A set of :math:`4\times4` matrices that
    # transform XYZ coordinates to the slice-coordinate system of (RO-PE-SS) and corresponding
    # list containing the registered blocks.
    _orientation_matrices_grad: dict[int, 'OMatrix']
    _orientation_matrices_rf: dict[int, ('OMatrix', int)]

    #: System specification object
    _system_specs: SystemSpec
    #:
    _blocks: List[SequenceBaseBlock]
    #:
    _block_lookup: Dict[str, SequenceBaseBlock]
    #:
    _reverse_block_lookup: Dict[id, str]


    def __init__(self, building_blocks: List[SequenceBaseBlock], system_specs: SystemSpec,
                 snap_to_raster: bool = False, copy: bool = False):

        self._system_specs = system_specs
        if copy:
            self._blocks = [b.copy() for b in building_blocks]
        else:
            self._blocks = building_blocks

        if snap_to_raster:
            [b.snap_to_raster(self._system_specs) for b in self._blocks]

        self._block_lookup = {}
        self._reverse_block_lookup = {}
        for block in self._blocks:
            self._add_unique_block_name(block)
        self._orientation_matrices_grad = {}
        self._orientation_matrices_rf = {}
        self.validate()

    def _ipython_key_completions_(self):
        return list(self._block_lookup.keys())

    def __add__(self, other: 'Sequence') -> 'Sequence':
        """ If both system specifications match, returns a new sequence containing deep copies
        of all blocks contained in self._blocks and other._blocks """
        self._check_sys_compatibility(other._system_specs)
        new_blocks = [deepcopy(b) for b in [*self._blocks, *other._blocks]]

        new_blocks = []
        new_orientation_matrices_grad = {}
        new_orientation_matrices_rf = {}
        for b in self._blocks:
            new_block = deepcopy(b)
            omatrix_grad = self._orientation_matrices_grad.get(id(b),None)
            omatrix_rf = self._orientation_matrices_rf.get(id(b),None)
            if omatrix_grad is not None:
                new_orientation_matrices_grad[id(new_block)] = omatrix_grad
            if omatrix_rf is not None:
                new_orientation_matrices_rf[id(new_block)] = omatrix_rf
            new_blocks.append(new_block)

        for b in other._blocks:
            new_block = deepcopy(b)
            omatrix_grad = other._orientation_matrices_grad.get(id(b),None)
            omatrix_rf = other._orientation_matrices_rf.get(id(b),None)
            if omatrix_grad is not None:
                new_orientation_matrices_grad[id(new_block)] = omatrix_grad
            if omatrix_rf is not None:
                new_orientation_matrices_rf[id(new_block)] = omatrix_rf
            new_blocks.append(new_block)
            
        new_seq = Sequence(new_blocks, system_specs=deepcopy(self._system_specs))
        new_seq._orientation_matrices_grad = new_orientation_matrices_grad
        new_seq._orientation_matrices_rf = new_orientation_matrices_rf
        return new_seq

    def __iadd__(self, other: "Sequence"):
        """ """
        self._check_sys_compatibility(other._system_specs)
        for b in other._blocks:
            self._add_unique_block_name(b)
            self._blocks.append(b)
        # Merge omatrix dicts
        self._orientation_matrices_grad = {**self._orientation_matrices_grad, **other._orientation_matrices_grad}
        self._orientation_matrices_rf = {**self._orientation_matrices_rf, **other._orientation_matrices_rf}
        return self

    def __getitem__(self, item: Union[str, int, slice, tuple]):
        """ Possible ways to index/query blocks in a sequence:

        .. code::

            seq[0], seq[0:4], seq[(0, 4, 1)] -> returns block by index assuming ordering
                        according to start time

            seq["trapezoidal_0"] -> returns block by name

        :param item:
        :return:
        """
        if isinstance(item, str):
            return self._block_lookup[item]
        elif isinstance(item, int):
            names_and_times = self._create_sorted_block_list(reversed=False)
            return self._block_lookup[names_and_times[item][0]]
        elif isinstance(item, slice):
            names_and_times = self._create_sorted_block_list(reversed=False)
            return [self._block_lookup[k] for k, _ in names_and_times[item]]
        elif isinstance(item, tuple):
            if not all([isinstance(i, int) for i in item]):
                raise NotImplementedError("When indexing with a tuple, all tuple entries must"
                                          f" be of type int. But got {item}!")
            names_and_times = self._create_sorted_block_list(reversed=False)
            return [self._block_lookup[names_and_times[i][0]] for i in item]
        else:
            raise NotImplementedError(f"{type(item)} is not in the list of possible block"
                                      f" queries [str, int, slice, Tuple[int]]")

    def __iter__(self):
        """Returns an iterator yielding blocks sorted by theirs start time"""
        start_times = self._create_sorted_block_list(reversed=False)
        return (self._block_lookup[k] for (k, _) in start_times)

    def items(self):
        """Returns a generator yielding (unique_block_name, block) tuples"""
        names_and_times = self._create_sorted_block_list(reversed=False)
        return ((k, self._block_lookup[k]) for (k, _) in names_and_times)

    def _add_unique_block_name(self, block: SequenceBaseBlock):
        """Iterates over block names and adds a counter to the block name if it already is used to
        create the dictionary (unique_block_name -> SequenceBaseBlock)
        :param block:
        """
        i = 0
        augmented_name = block.name + f"_{i}"
        while self._block_lookup.get(augmented_name, None) is not None:
            augmented_name = block.name + f"_{i}"
            i += 1
        self._block_lookup.update({augmented_name: block})
        self._reverse_block_lookup.update({id(block): augmented_name})

    def _check_sys_compatibility(self, system_specs: SystemSpec):
        equalities = [self._system_specs.__dict__[k] == system_specs.__dict__[k]
                      for k in self._system_specs.__dict__.keys()]
        if not all(equalities):
            raise ValueError("System specifications of added sequence do not match. Addition "
                             "for different system specifications is not implemented")

    def _create_sorted_block_list(self, reversed: bool = False):
        start_times = [(k, b.tmin) for k, b in self._block_lookup.items()]
        start_times.sort(key=lambda x: float(x[1].m_as("ms")), reverse=reversed)
        return start_times

    def validate(self) -> None:
        """ Calls the validation function of each block with self._system_specs

        :raises ValueError: If any contained block fails to validate with own system specs
        :raises ValueError: If any combination of contained acquisition blocks have temporal
                            overlap.
        :raise ValueError: If all combined gradient definitions exceed system limits (max amplitude
                           and slew-rate)
        """
        for block in self._blocks:
            try:
                block.validate(system_specs=self._system_specs)
            except ValueError as err:
                unique_name = self._reverse_block_lookup[id(block)]
                err.args = (f'While validation of bock {unique_name}: \n\t' + err.args[0],)
                raise err

        self._validate_combined_gradient_limits()
        self._validate_overlap(ADC, self._system_specs.adc_dead_time)
        self._validate_overlap(RFPulse, self._system_specs.rf_dead_time)
        self._validate_overlapping_rf_adc()

    def _validate_overlapping_rf_adc(self):
        """Checks if RF and ADC are occurring simultaneously in case it is not explicitly
        allowed in the system. This includes the RF ring down time as minimal distance between
        a RF pulse and the

        :return:
        """
        if not self._system_specs.enable_simulatenous_trasmit_receive:
            all_blocks = self.get_block(typedef=[ADC, RFPulse])
            start_end = [(block.tmin.m_as("ms"), block.tmax.m_as("ms")) for block in all_blocks]

            if start_end:
                start_end = np.array(start_end)
                sort_idcs = np.argsort(start_end[:, 0])
                start_end = start_end[sort_idcs]
                all_blocks = [all_blocks[i] for i in sort_idcs]
                current_rf_end = start_end[0, 0] - self._system_specs.rf_ringdown_time.m_as("ms")
                current_adc_end = start_end[0, 0]
                for idx, (tmin, tmax) in enumerate(start_end):
                    if isinstance(all_blocks[idx], RFPulse):
                        if not current_adc_end <= tmin:
                            _msg = (f"RF block {self._reverse_block_lookup[id(all_blocks[idx])]} "
                                    f"starts before {self._reverse_block_lookup[id(all_blocks[idx - 1])]} "
                                    f"ends, while simultaneous TR is not allowed.")
                            raise ValueError(_msg)
                        current_rf_end = tmax
                    if isinstance(all_blocks[idx], ADC):
                        if not current_rf_end + self._system_specs.rf_ringdown_time.m_as(
                                "ms") <= tmin:
                            raise ValueError(
                                f"ADC block {self._reverse_block_lookup[id(all_blocks[idx])]} "
                                f"starts before {self._reverse_block_lookup[id(all_blocks[idx - 1])]} "
                                f"ends, while simultaneous TR is not allowed.")
                        current_adc_end = tmax

    def _validate_overlap(self, typedef, dead_time: Quantity):
        """ Checks for any temporal overlap of contained <typedef> blocks.
        This assumes only one <typedef> can be active at the same time, and consecutive blocks
        must be at least <dead_time> apart.
        :param typedef: either ADC or RF
        """
        all_blocks = self.get_block(typedef=typedef)
        start_end = [(block.tmin.m_as("ms"), block.tmax.m_as("ms")) for block in all_blocks]

        if start_end:
            start_end = np.array(start_end)
            sort_idcs = np.argsort(start_end[:, 0])
            all_blocks = [all_blocks[i] for i in sort_idcs]
            gaps = start_end[:, 0][sort_idcs][1:] - start_end[:, 1][sort_idcs][:1]
            non_overlap = np.greater_equal(gaps, dead_time.m_as("ms"))

            if not np.all(non_overlap):
                violating_indices = np.where(np.logical_not(non_overlap))[0]
                violating_blocks = [(all_blocks[i], all_blocks[i + 1]) for i in violating_indices]
                error_string = "\n\t".join([
                    " and ".join([self._reverse_block_lookup[id(b)] for b in blocks]) +
                    f"({blocks[0].tmin} - {blocks[0].tmax}) and "
                    f"({blocks[1].tmin} - {blocks[1].tmax})"
                    for blocks in violating_blocks])
                raise ValueError(f"Detected overlapping blocks with dead-time ({dead_time}):"
                                 "\n\t" + error_string)

    def _validate_combined_gradient_limits(self):
        """Combines all contained gradient definitions and checks if slew rate and max grad are
        within system limits. Otherwise, raises ValueError.
        """
        if self.get_block(typedef=Gradient):
            time_grid, waveform = self.combined_gradients()
            max_slew_rate = np.max(np.diff(waveform, axis=1) / np.diff(time_grid)[np.newaxis],
                                   axis=1)
            max_grad = np.max(waveform, axis=1)
            if not np.all(np.less_equal(np.abs(max_grad),
                                        self._system_specs.max_grad.m_as("mT/m") + 1e-12)):
                raise ValueError(f"Combined gradients exceed system limits ({max_grad} "
                                 f"> {self._system_specs.max_grad.m_as('mT/m')})")

            if not np.all(np.less_equal(np.abs(max_slew_rate),
                                        self._system_specs.max_slew.m_as("mT/m/ms") + 1e-12)):
                raise ValueError(f"Combined gradients exceed system limits ({max_slew_rate} "
                                 f"> {self._system_specs.max_slew.m_as('mT/m/ms')})")

    def add_block(self, block: SequenceBaseBlock, copy: bool = True) -> None:
        """ Add the instance of block to the internal List of sequence blocks.

        **Note**: The internal definition of blocks is mutable, therefore if the new block is not
        copied, subsequent alterations can have unwanted side-effects inside the sequence.

        :raises ValueError: If block.validate() fails to validate using the system specs of self
        :raises TypeError: If block is an instance of class SequenceBaseBlock

        :param block: Sequence block to be added to the sequence
        :param copy: Determines if the block is copied before adding it to the sequence
        """

        if not isinstance(block, SequenceBaseBlock):
            raise NotImplementedError("Method only defined for instances of SequenceBaseBlocks."
                                      f"Got {type(block)}")
        try:
            block.validate(self._system_specs)
        except ValueError as err:
            raise ValueError("New block does not validate against sequence system specifications."
                             f"Resulting in following ValueError: {err}") from err
        if copy:
            block = deepcopy(block)
        self._blocks.append(block)
        self._add_unique_block_name(block)

    def rename_blocks(self, old_names: List[str], new_names: List[str]):
        """ Renames blocks and updates block lookup map"""
        for old, new in zip(old_names, new_names):
            bl = self._block_lookup[old]
            bl.name = new
        self._block_lookup = {}
        for block in self._blocks:
            self._add_unique_block_name(block)

    def remove_block(self, block_name: str):
        """ Removes block from internal lookup """
        block = self.get_block(block_name)
        if block is None:
            raise ValueError(f"Tried to remove non-existing block; \n "
                             f"'{block_name}' not in {self.blocks}")
        block_index = [block is b for b in self._blocks].index(True)
        del self._blocks[block_index]
        del self._block_lookup[block_name]
        del self._reverse_block_lookup[id(block)]
        if self._orientation_matrices_grad.get(id(block), None) is not None:
            del self._orientation_matrices_grad[id(block)]
        if self._orientation_matrices_rf.get(id(block), None) is not None:
            del self._orientation_matrices_rf[id(block)]

    def append(self, other: Union['Sequence', SequenceBaseBlock],
               copy: bool = True, end_time: Quantity = None) -> None:
        """If both system specifications match, copies all blocks from `other`, shifts them by the
        current end time of this sequence intance (plus an additional delay according to ADC/RF -
        dead times and RF-ring-down time) and adds the blocks to itself.

        :raises ValueError: If other fails to validate using the system specs of self

        :param other: Sequence or block to be added to the sequence
        :param copy: if true copies the other sequence object
        :param end_time:
        """
        if isinstance(other, SequenceBaseBlock):
            try:
                other.validate(self._system_specs)
            except ValueError as err:
                raise ValueError(
                    "New block does not validate against sequence system specifications."
                    f"Resulting in following ValueError: {err}") from err
            block_copies = [other, ]
        elif isinstance(other, Sequence):
            self._check_sys_compatibility(other._system_specs)  # pylint: disable=W0212
            block_copies = [other.get_block(block_name) for block_name in other.blocks]
            ids = [id(block) for block in block_copies] # list of IDs for transfering o-matrices
        else:
            raise NotImplementedError(f"Cannot append object of type {type(other)} to Sequence")

        if copy:
            block_copies = [deepcopy(block) for block in block_copies]

        if end_time is None:
            if not self._blocks:
                end_time = Quantity(0., "ms")
            else:
                end_time = self._get_append_delay(other)

        for block in block_copies:
            block.shift(Quantity(end_time, "ms"))

        self._blocks.extend(block_copies)
        if isinstance(other, Sequence):
            for block,blid in zip(block_copies,ids):
                self._add_unique_block_name(block)
                # Update omatrix dicts
                if blid in other._orientation_matrices_grad:
                    self._orientation_matrices_grad[id(block)] = other._orientation_matrices_grad[blid]
                if blid in other._orientation_matrices_rf:
                    self._orientation_matrices_rf[id(block)] = other._orientation_matrices_rf[blid]
        else:
            for block in block_copies:
                self._add_unique_block_name(block)

    def extend(self, other: typing_Sequence[Union['Sequence', SequenceBaseBlock]],
               copy: bool = True) -> None:
        """If both system specifications match, copies all blocks from `other` shifts them by own
        tmax and adds the blocks to own collection

        :raises ValueError: If other fails to validate using the system specs of self

        :param other: ListSequence or block to be added to the sequence
        :param copy: if true copies the other sequence object
        """
        end_times = [self._get_append_delay(other[0]).m_as("ms"), ]
        end_times.extend([bl._get_append_delay(br).m_as("ms") if isinstance(bl, Sequence)
                          else Sequence([bl], self._system_specs)._get_append_delay(br).m_as("ms")
                          for bl, br in zip(other[:-1], other[1:])])
        end_times = np.round(end_times,4) # 100 ns rounding
        end_times = Quantity(np.round(np.cumsum(end_times),4), "ms")
        for idx, other_it in enumerate(tqdm(other, desc="Extending Sequence")):
            self.append(other_it, copy, end_time=end_times[idx])

    def _get_append_delay(self, other: Union['Sequence', SequenceBaseBlock]):
        """Calculates the minimum shift for the other object based on system limits.

        If no dead-times and ring-down time is specified the minimum shift is trivially the end
        of self. Otherwise, this method evaluates:
        a. Distance between the end of self last adc and start of other first adc
        b. Distance between the end of self last rf and start of other first rf
        c. (if simultaneous transmit/receive is not enabled) Distance between end of self last rf
            and start of other first adc

        Then it checks 1, 2, 3 against the system limits:
        1. If a) is smaller than adc dead time an additional minimum delay of deadtime is set
        2. If b) is smaller than rf dead time an additional minimum delay of deadtime is set
        3. If c) is smaller than rf ring down an additional minimum delay of ring-down is set

        finally as overall shift return self.end + max(1., 2., 3.)
        """

        if not any([self._system_specs.adc_dead_time.m_as("ms") > 0.,
                    self._system_specs.rf_ringdown_time.m_as("ms") > 0.,
                    self._system_specs.rf_dead_time.m_as("ms") > 0.,
                    self._system_specs.rf_lead_time.m_as("ms") > 0.]):
            return self.end_time

        if isinstance(other, Gradient):
            return self.end_time

        last_rf_self = self.get_block(typedef=RFPulse, sort_by="end")
        if not last_rf_self:
            last_rf_self = self.start_time.m_as("ms")
        else:
            last_rf_self = last_rf_self[-1].tmax.m_as("ms")

        last_adc_self = self.get_block(typedef=ADC, sort_by="end")
        if last_adc_self:
            last_adc_self = last_adc_self[-1].tmax.m_as("ms")
        else:
            last_adc_self = self.start_time.m_as("ms")
        end_self = self.end_time.m_as("ms")

        if isinstance(other, RFPulse):
            rf_dead_time_shift = min(last_rf_self + other.tmin.m_as("ms"),
                                     self._system_specs.rf_dead_time.m_as("ms"))
            rf_lead_time_shift = min(last_adc_self + other.tmin.m_as("ms"),
                                     self._system_specs.rf_lead_time.m_as("ms"))
            shift = max(rf_dead_time_shift, rf_lead_time_shift)
            return Quantity(shift + end_self, "ms")
        elif isinstance(other, ADC):
            shift = min(last_adc_self + other.tmin.m_as("ms"),
                        self._system_specs.adc_dead_time.m_as("ms"))
            if not self._system_specs.enable_simulatenous_trasmit_receive:
                ring_down_shift = min(last_rf_self + other.tmin.m_as("ms"),
                                      self._system_specs.rf_ringdown_time.m_as("ms"))
                shift = max(ring_down_shift, shift)
            return Quantity(shift + end_self, "ms")

        elif isinstance(other, Sequence):
            first_rf_other = other.get_block(typedef=RFPulse, sort_by="start")
            if first_rf_other:
                first_rf_other = first_rf_other[0].tmin.m_as("ms")
                current_gap_rfdead = end_self - last_rf_self + first_rf_other
                if current_gap_rfdead > self._system_specs.rf_dead_time.m_as("ms"):
                    min_rfdead = 0.
                else:
                    min_rfdead = self._system_specs.rf_dead_time.m_as("ms") - current_gap_rfdead

                current_gap_rflead = end_self - last_adc_self + first_rf_other
                if current_gap_rflead > self._system_specs.rf_lead_time.m_as("ms"):
                    min_rflead = 0.
                else:
                    min_rflead = self._system_specs.rf_lead_time.m_as("ms") - current_gap_rflead
            else:
                min_rfdead = 0.
                min_rflead = 0.

            first_adc_other = other.get_block(typedef=ADC, sort_by="start")
            if first_adc_other:
                first_adc_other = first_adc_other[0].tmin.m_as("ms")
                current_gap = end_self - last_adc_self + first_adc_other
                if current_gap > self._system_specs.adc_dead_time.m_as("ms"):
                    min_adcdead = 0.
                else:
                    min_adcdead = self._system_specs.adc_dead_time.m_as("ms") - current_gap
            else:
                min_adcdead = 0.

            if self._system_specs.enable_simulatenous_trasmit_receive:
                min_rfringdown = 0.
            else:
                current_gap = end_self - last_rf_self + first_adc_other
                if current_gap > self._system_specs.rf_ringdown_time.m_as("ms"):
                    min_rfringdown = 0.
                else:
                    min_rfringdown = self._system_specs.rf_ringdown_time.m_as("ms") - current_gap

            shift = max(min_adcdead, min_rfdead, min_rfringdown, min_rflead)
            return Quantity(shift + end_self, "ms")
        else:
            return self.end_time

    def get_block(self, block_name: Union[str, Iterable[str]] = None,
                  partial_string_match: Union[str, Iterable[str]] = None,
                  regular_expression: Union[str, Iterable[str]] = None,
                  typedef=None,
                  invert_pattern: bool = False,
                  sort_by: str = None) \
            -> Union[SequenceBaseBlock, List[SequenceBaseBlock]]:
        """ Returns reference to the block whose member `name` matches the specified argument.
        If no block with given name is present in the sequence, it returns None

        .. note::

            Checks which keyword argument to use from left to right as specified in the signature.
            If multiple are specified uses only the first one.

        :raises: ValueError if no keyword-argument is specified

        :param block_name: String or iterable of strings exactly matching a set of blocks contained
                            in the sequence
        :param partial_string_match: str or iterable of strings that specify partial string matches.
                            All blocks partially matching at least one are returned.
        :param regular_expression: str or iterable of strings containing regular expressions that
                            are matched against the block-names. All blocks, matching at least one
                            of the given expressions are returned.
        :param typedef: type defintion (e.g. cmrseq.bausteine.ADC)
        :param invert_pattern: if True, all blocks except of the pattern-matched names are returned
        :param sort_by: from [None, start, end] returns the list of blocks sorted according to their
                        start or end time, is ignored if blocks are retrieved by name
        :return: SequenceBaseBlock or List of SequenceBaseBlocks depending on the specified argument
        """
        if block_name is not None:
            if isinstance(block_name, str):
                return self._block_lookup.get(block_name, None)
            return [self._block_lookup[bn] for bn in block_name]

        elif partial_string_match is not None:
            if isinstance(partial_string_match, str):
                partial_string_match = [partial_string_match, ]
            partial_string_match = "|".join([f"(?:.*{p}.*)" for p in partial_string_match])
            # The condition inside the list-comprehension corresponds to a XOR operation
            # (is_match XOR invert), to determine if matched blocks are included or skipped
            matched_blocks = [block for name, block in self._block_lookup.items()
                              if ((re.match(partial_string_match, name) is not None)
                                  ^ invert_pattern)]
        elif regular_expression is not None:
            if isinstance(regular_expression, str):
                regular_expression = [regular_expression, ]
            regular_expression = "|".join([f"(?:{p})" for p in regular_expression])
            # The condition inside the list-comprehension corresponds to a XOR operation
            # (is_match XOR invert), to determine if matched blocks are included or skipped
            matched_blocks = [block for name, block in self._block_lookup.items()
                              if ((re.match(regular_expression, name) is not None)
                                  ^ invert_pattern)]

        elif typedef is not None:
            if not isinstance(typedef, (list, tuple)):
                typedef = (typedef,)
            typedef = tuple(typedef)
            matched_blocks = [block for name, block in self._block_lookup.items()
                              if (isinstance(block, typedef) ^ invert_pattern)]
        else:
            raise ValueError("At least one on the keyword arguments must be specified")

        if sort_by is not None:
            match sort_by:
                case "start":
                    tmins = np.array([b.tmin.m_as("ms") for b in matched_blocks])
                    indices = np.argsort(tmins)
                    matched_blocks = [matched_blocks[i] for i in indices]
                case "end":
                    tmax = np.array([b.tmax.m_as("ms") for b in matched_blocks])
                    indices = np.argsort(tmax)
                    matched_blocks = [matched_blocks[i] for i in indices]
                case _:
                    raise NotImplementedError(f"Specified sorting ({sort_by}) is not implemented")

        return matched_blocks

    def register_omatrix(self, matrix: 'OMatrix', gradients: list[Union[str, Gradient]] = None,
                         rf_pulses: list[
                             tuple[Union[str, RFPulse], Union[str, TrapezoidalGradient]]] = None):
        """Updates the mapping of orientation matrix objects for given Gradient blocks and
        rf_pulses associated with a slice-selection gradients

        :param matrix: cmrseq.OMatrix object
        :param gradients: List of unique block names or instances of type Gradient to be registered
                            with the given o-matrix
        :param rf_pulses: List of tuples containing block-names or instances of
                    (RF-pulse, TrapezoidalGradients), to be registered with the orientation matrix
        """
        if gradients is not None:
            for bn in gradients:
                if isinstance(bn, str):
                    bn: SequenceBaseBlock = self._block_lookup[bn]
                else:
                    assert self._reverse_block_lookup.get(id(bn), None) is not None
                self._orientation_matrices_grad[id(bn)] = matrix

        if rf_pulses is not None:
            for rf_block, trap_block in rf_pulses:
                if isinstance(rf_block, str):
                    rf_block: SequenceBaseBlock = self._block_lookup[rf_block]
                else:
                    assert self._reverse_block_lookup.get(id(rf_block), None) is not None
                if isinstance(trap_block, str):
                    trap_block: SequenceBaseBlock = self._block_lookup[trap_block]
                else:
                    assert self._reverse_block_lookup.get(id(trap_block), None) is not None

                assert isinstance(rf_block, RFPulse) and isinstance(trap_block, TrapezoidalGradient)
                self._orientation_matrices_rf[id(rf_block)] = (matrix, trap_block)

    def shift_in_time(self, shift: Quantity) -> None:
        """ Shifts all blocks contained in the sequence object by the specified time

        :param shift: Quantity of dimesion time
        """
        for block in self._blocks:
            block.shift(time_shift=shift)

    def time_reverse(self) -> None:
        """ Reverses the sequence in time
        """
        # flip about end of sequence
        time_flip_point = self.duration
        for block in self._blocks:
            block.flip(time_flip_point)

    @property
    def duration(self) -> Quantity:
        """Time difference of earliest start and latest end of all blocks contained in the sequence
        """
        return self.end_time - self.start_time

    @property
    def start_time(self):
        """Returns temporal minimum of all contained block definitions"""
        all_min = [b.tmin.m_as("ms") for b in self._blocks]
        if not all_min:
            all_min = [0.]
        return Quantity(np.round(np.min(all_min), 6), 'ms')

    @property
    def end_time(self):
        """Returns temporal maximum of all contained block definitions"""
        all_max = [b.tmax.m_as("ms") for b in self._blocks]
        if not all_max:
            all_max = [0.]
        return Quantity(np.round(np.max(all_max), 6), 'ms')

    @property
    def gradients(self) -> List[Tuple[Quantity, Quantity]]:
        """ Returns the gradient definitions (t, wf) of all Gradient-type blocks that are
         contained in the sequence. If an OMatrix is registered the gradient channels are
         rotated accordingly by applying the OMatrix object"""
        gradient_blocks = self.get_block(typedef=Gradient)
        result = []
        for block in gradient_blocks:
            if (omat := self._orientation_matrices_grad.get(id(block), None)) is not None:
                result.append(omat.apply(block))
            else:
                result.append(block.gradients)
        return result
        # return [block.gradients for block in self._blocks if isinstance(block, Gradient)]

    @property
    # pylint: disable=C0103
    def rf(self) -> List[Tuple[Quantity, Quantity]]:
        """Returns the rf definitions (t, amplitude) of RFPulse-type blocks that are contained in
        the sequence. If an OMatrix is registered the frequency offset is adjusted accordingly
        by applying the OMatrix object"""
        rf_blocks = self.get_block(typedef=RFPulse)
        result = []
        for block in rf_blocks:
            omat, trap = self._orientation_matrices_rf.get(id(block), (None, None))
            if omat is not None:
                result.append(omat.apply([block, trap]))
            else:
                result.append(block.rf)
        return result

    @property
    def rf_events(self) -> List[Tuple[Quantity, Quantity]]:
        """Returns the rf events (rf-center, flip-angle) of RFPulse-type blocks that are contained
        in the sequence. """
        rf_blocks = self.get_block(typedef=RFPulse)
        return [block.rf_events for block in rf_blocks]

    @property
    def adc_centers(self) -> List[Quantity]:
        """ Returns the centers of all adc_blocks in the sequence."""
        return [block.adc_center for block in self._blocks if isinstance(block, ADC)]

    @property
    def blocks(self) -> List[str]:
        """Returns a tuple containing the names of all blocks contained in the sequence object,
        where temporal ordering is assumed"""
        names_and_times = self._create_sorted_block_list(reversed=False)
        names = [n for n, t in names_and_times]
        return names

    def __deepcopy__(self, memo={}) -> 'Sequence':
        """ Returns deepcopy of the sequence object"""

        cls = self.__class__
        new_seq = cls.__new__(cls)
        memo[id(self)] = new_seq
        for k, v in self.__dict__.items():
            setattr(new_seq, k, deepcopy(v, memo))

        new_seq._reverse_block_lookup.update({id(new_seq._block_lookup[n]): n
                                              for n in new_seq.blocks})

        # The o-mat mappings must be updated with the ids of the new block instances
        new_seq._orientation_matrices_grad = {}
        for id_, omat in self._orientation_matrices_grad.items():
            new_seq._orientation_matrices_grad.update({
                id(new_seq._block_lookup[self._reverse_block_lookup[id_]]): omat})
        for id_, (omat, trap) in self._orientation_matrices_rf.items():
            new_seq._orientation_matrices_rf.update({
                id(new_seq._block_lookup[self._reverse_block_lookup[id_]]):
                    (omat, new_seq._block_lookup[self._reverse_block_lookup[id(trap)]])})
        return new_seq

    def copy(self) -> 'Sequence':
        return deepcopy(self)
    
    def partial_sequence(self, copy_blocks: bool,
                         partial_string_match: Union[str, Iterable[str]] = None,
                         regular_expression: Union[str, Iterable[str]] = None,
                         invert_pattern: bool = False, **kwargs) -> 'Sequence':
        """Returns a cmrseq.Sequence object containing references or deep-copies of all blocks
        matched either with partial-string-match or regular expressions specified as keyword
         argument.

        :param copy_blocks: if True, creates deep-copies of matched blocks.
        :param partial_string_match: str or iterable of strings that specify partial string matches.
                    All blocks partially matching at least one are returned.
        :param regular_expression: str or iterable of strings containing regular expressions that
                            are matched against the block-names. All blocks, matching at least one
                            of the given expressions are returned.
        :param invert_pattern: if True, all blocks except of the pattern-matched names are returned
        :return: Sequence object
        """
        matched_blocks = self.get_block(block_name=None, partial_string_match=partial_string_match,
                                        regular_expression=regular_expression,
                                        invert_pattern=invert_pattern)
        return Sequence(building_blocks=matched_blocks, system_specs=self._system_specs,
                        copy=copy_blocks, **kwargs)

    # pylint: disable=R0914, C0103
    def gradients_to_grid(self, start_time: Quantity = None) -> Tuple[np.ndarray, np.ndarray]:
        """ Grids gradient definitions of all blocks contained in the sequence, on a joint time grid
        from the minimal to maximal value in single time-points definitions with a step-length
        defined in system_specs.grad_raster_time.
        If gradients occur at the same time on the same channel, they are added.

        :return: (np.ndarray, np.ndarray) of shape (t, ) containing the time-grid and
            (3 [gx, gy, gz], t) containing the waveform definition in ms and mT/m
            returns (None, None) if no gradients are contained in the sequence
        """

        gradients = self.gradients
        if not gradients:
            return None, None

        time_points = [g[0].m_as("ms") for g in gradients]
        wave_forms = [g[1].m_as("mT/m") for g in gradients]

        if start_time is None:
            start_time = self.start_time.m_as("ms")
        end_time = self.end_time.m_as("ms")

        dt = self._system_specs.grad_raster_time.m_as("ms")
        t_grid = np.arange(start_time, end_time + dt, dt)
        wf_grid = np.zeros((3, t_grid.shape[0]))

        for t, wf, bidx in zip(time_points, wave_forms, range(len(self._blocks))):
            t = np.array(t)
            tidx = np.around((t - start_time) / dt)
            if not np.allclose((t - start_time) / dt, tidx, rtol=1e-6):
                warn(
                    f"Sequence.gradient_to_grid: Gradient definition of block {bidx} is not on gradient raster")
            start, end = int(tidx[0]), int(tidx[-1])
            interpolated_wfx = np.interp(t_grid[start:end], t, wf[0])
            interpolated_wfy = np.interp(t_grid[start:end], t, wf[1])
            interpolated_wfz = np.interp(t_grid[start:end], t, wf[2])
            wf_grid[:, start:end] += np.stack([interpolated_wfx,
                                               interpolated_wfy,
                                               interpolated_wfz])
        return t_grid, wf_grid

    def combined_gradients(self) -> Tuple[np.ndarray, np.ndarray]:
        """ Combines the gradient definitions of all blocks contained in the sequence,
        into a joint single definition. The joint time-points are defined by the set of unique
        time-points of all combined blocks.
        If gradients occur at the same time on the same channel, they are added.

        :return: (np.ndarray, np.ndarray) of shape (t, ) containing the time-points and
            (3 [gx, gy, gz], t) containing the waveform definition in ms and mT/m
            returns (None, None) if no gradients are contained in the sequence
        """

        gradients = self.gradients
        if not gradients:
            return None, None

        time_points = [g[0].m_as("ms") for g in gradients]
        wave_forms = [g[1].m_as("mT/m") for g in gradients]

        t_grid = np.sort(np.unique(np.around(np.concatenate(time_points, axis=0), decimals=4)))
        t_grid = np.round(t_grid, decimals=4) # round to 4 decimals (100 ns)
        wf_grid = np.zeros((3, t_grid.shape[0]))

        t_idx = np.searchsorted(t_grid, np.concatenate(time_points)).tolist()

        for t, wf in zip(time_points, wave_forms):
            t = np.round(t, decimals=4) # round to 4 decimals (100 ns)
            t_idx_tmp = t_idx[:len(t)]
            del t_idx[:len(t)]
            start, end = int(t_idx_tmp[0]), int(t_idx_tmp[-1])
            interpolated_wfx = np.interp(t_grid[start:end], t, wf[0])
            interpolated_wfy = np.interp(t_grid[start:end], t, wf[1])
            interpolated_wfz = np.interp(t_grid[start:end], t, wf[2])
            wf_grid[:, start:end] += np.stack([interpolated_wfx,
                                               interpolated_wfy,
                                               interpolated_wfz])

        return t_grid, wf_grid

    def combined_rf(self) -> Tuple[np.ndarray, np.ndarray]:
        """Combines the rf-definitions of all blocks contained in the sequence,
        into a joint single definition. The joint time-points are defined by the set of unique
        time-points of all combined blocks.
        If rf occur at the same time they are added.

        :return: (np.ndarray, np.ndarray) of shape (t, ) containing the time-points and
            (t, ) containing the complex RF-waveform definition in ms and uT

        """
        rf_waveforms = self.rf
        if not rf_waveforms:
            return None, None

        time_points = [r[0].m_as("ms") for r in rf_waveforms]
        wave_forms = [np.stack([r[1].m_as("uT").real, r[1].m_as("uT").imag]) for r in rf_waveforms]

        t_grid = np.sort(np.unique(np.concatenate(time_points, axis=0)))
        wf_grid = np.zeros(t_grid.shape[0], dtype=np.complex128)
        t_idx = np.searchsorted(t_grid, np.concatenate(time_points)).tolist()

        for t, wf in zip(time_points, wave_forms):
            t_idx_tmp = t_idx[:len(t)]
            del t_idx[:len(t)]
            start, end = int(t_idx_tmp[0]), int(t_idx_tmp[-1])
            interpolated_wfreal = np.interp(t_grid[start:end], t, wf[0])
            interpolated_wfimag = np.interp(t_grid[start:end], t, wf[1])
            wf_grid[start:end] += interpolated_wfreal + 1j * interpolated_wfimag
        return t_grid, wf_grid

    # pylint: disable=R0914, C0103
    def rf_to_grid(self) -> Tuple[np.ndarray, np.ndarray]:
        """ Grids RF-definitions of all blocks contained in the sequence, on a joint time grid
        from the minimal to maximal value in single time-points definitions with a step-length
        defined in system_specs.rf_raster_time.

        If RF-pulses occur at the same time on the same channel, they are added.

        :return: (np.ndarray, np.ndarray) of shape (1, t) containing the time-grid and
                (1, t) containing the complex RF amplitude
        """
        rf = self.rf
        if not rf:
            return None, None

        time_points = [r[0].m_as("ms") for r in rf]
        wave_forms = [r[1].m_as("mT") for r in rf]

        start_time = self.start_time.m_as("ms")
        end_time = self.end_time.m_as("ms")

        dt = self._system_specs.rf_raster_time.m_as("ms")
        t_grid = np.arange(start_time, end_time + dt, dt)
        rf_grid = np.zeros((t_grid.shape[0]), dtype=np.complex64)

        for t, complex_alpha, bidx in zip(time_points, wave_forms, range(len(rf))):
            t = np.array(t)
            tidx = np.around((t - start_time) / dt)
            if not np.allclose((t - start_time) / dt, tidx, atol=1e-6):
                warn(f"Sequence.rf_to_grid: RF definition of block {bidx} is not on RF raster")
            start, end = int(tidx[0]), int(tidx[-1])
            rf_grid[start:end] += np.interp(t_grid[start:end], t, complex_alpha)
        return t_grid, rf_grid

    def combined_adc(self) -> Tuple[np.ndarray, np.ndarray]:
        """Combines all ADC-type blocks contained in the sequence, on a joint time grid.

        **Note**: The binary event channel of the returned array is technically not needed but adheres to the signature
                    of dense gridding

        :return: - Array of shape (t, ) containing the time-points
                 - Array of shape (t, 2) containing binary event and phase
        """
        # First grid all individual blocks on adc_raster times
        adc_blocks = [block for block in self._blocks if isinstance(block, ADC)]
        t_combined = []
        adc_def_combined = []
        for block in adc_blocks:
            t_ = block.adc_timing.m_as("ms")
            on = np.ones_like(t_)
            phase = block.adc_phase
            t_combined.append(t_)
            adc_def_combined.append(np.stack([on, phase], axis=1))

        # insert into common array
        t_combined = np.concatenate(t_combined, axis=0)
        adc_def = np.concatenate(adc_def_combined, axis=0)
        sorting_indices = np.argsort(t_combined)
        return t_combined[sorting_indices], adc_def[sorting_indices, :]

    # pylint: disable=R0914, C0103
    def adc_to_grid(self, force_raster: bool = False) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Grids the ADC-Events of all blocks contained in the sequence as boolean 1D mask along
        with the resulting time-grid. Additionally, the start and end points of the all adc-blocks
        are returned. The definition of start/end differ for force_gradient_raster True/False

        **Boolean mask explanation**:

            - *force_raster* == `False`
                                events that are not defined on the grid, are inserted into the
                                time-raster resulting in a non-uniform time definition.
                                The boolean values of the newly inserted points are set to 1.
            - *force_raster* == `True`
                                for events that are not defined on the grid the boolean values
                                of the interval borders on gradient raster time are set to 1.
                                For events that are already on the grid, the corresponding single
                                index is set 1.

        **Start/End - definition**:

            - *force_raster* == `False`:
                the exact time of first/last event per block is returned.
            - *force_raster* == `True`:
                The returned start/end times correspond to the beginning and end of the plateau
                of a trapezoidal gradient played out during the adc-events (addition of dwell-time).

        :param force_raster: bool - defaults to True
        :return: Tuple(np.array, np.array, np.array)
                      - (t, ) containing time-values
                      - (t, ) containing values of 0 or 1, indicating where the adc is active
                      - (t, ) containing the adc_phase in radians
                      - (#adc_blocks, 2) where (:, 0) contains the indices of the start time of
                        the adc-block and (:, 1) the end time correspondingly.
        """
        # First grid all individual blocks on adc_raster times
        adc_blocks = [block for block in self._blocks if isinstance(block, ADC)]
        gridded_adcs = []
        for block in adc_blocks:
            gridded_adcs.append(self._grid_single_adc_block(force_raster, block))

        # Secondly Insert the gridded adc-timings into the gradient raster
        gradient_raster = self.gradients_to_grid()[0]

        # Make sure that all gridded adc times are within the boundaries of gradient_raster because
        # Otherwise the insertion logic below will fail
        latest_adc_raster_time = np.max([np.max(t[0]) for t in gridded_adcs])
        first_adc_raster_time = np.min([np.min(t[0]) for t in gridded_adcs])
        if gradient_raster is None:
            gradient_raster = np.arange(first_adc_raster_time, latest_adc_raster_time,
                                        self._system_specs.grad_raster_time.m_as("ms"))
        if gradient_raster[-1] <= latest_adc_raster_time:
            gradient_raster = np.append(gradient_raster, latest_adc_raster_time)

        # Concatenate gridded adcs, sort the adcs according to their initial value of t
        gridded_adcs.sort(key=lambda v: v[0][0])
        adc_raster_time = np.around(np.concatenate([v[0] for v in gridded_adcs]), decimals=6)
        adc_on = np.concatenate([v[1] for v in gridded_adcs])
        adc_phase = np.concatenate([v[2] for v in gridded_adcs])
        if not np.all(np.diff(adc_raster_time) >= 0):
            raise ValueError("Currently gridding sequences with ADCs is only possible for "
                             "non-overlapping ADC-blocks")

        # Find positions to insert
        gradient_raster = np.around(gradient_raster, decimals=6)
        insertion_idx = np.searchsorted(gradient_raster, adc_raster_time, side="left")

        # Insert points into time raster and allocate the adc_on/phase arrays
        # while ignore points that are already on the gradient raster
        gradient_raster = np.insert(gradient_raster, insertion_idx, adc_raster_time)
        gradient_raster = np.unique(np.around(gradient_raster, decimals=6))
        adc_activation_raster = np.zeros_like(gradient_raster)
        adc_phase_raster = np.zeros_like(gradient_raster)

        # Recalculate indices to set values for phase and activation and set values accordingly
        setting_idx = np.searchsorted(gradient_raster, adc_raster_time, side="left")
        adc_activation_raster[setting_idx] = adc_on
        adc_phase_raster[np.where(adc_activation_raster)] = adc_phase
        start_end_per_event = []
        for time_raster, _, _ in gridded_adcs:
            s_e = np.searchsorted(gradient_raster, np.stack([time_raster[0], time_raster[-1]]))
            start_end_per_event.append(s_e)
        start_end_per_event = np.stack(start_end_per_event)

        return gradient_raster, adc_activation_raster, adc_phase_raster, start_end_per_event

    def _grid_single_adc_block(self, force_raster: bool, block: ADC, include_ADCoff: bool=False) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """ Grids a single adc-block to raster

        :param force_raster: bool
        :param block: Block that is a subclass of cmrseq.bausteine.ADC
        :param include_ADCoff: bool, if False only points where ADC is on are included
        :return: (time_raster, adc_activation_raster, adc_phase_raster)
        """

        rounded_adc_timings = np.around(block.adc_timing.m_as("ms"), decimals=6)
        dt = np.round(self._system_specs.adc_raster_time.m_as("ms"), decimals=6)
        time_raster = np.around(np.arange(block.tmin.m_as("ms"), block.tmax.m_as("ms") + dt, dt),
                                decimals=6)
        phase = block.adc_phase

        if not include_ADCoff:
            if force_raster:
                rounded_adc_timings = dt*np.round(rounded_adc_timings / dt)  
            
            return np.around(rounded_adc_timings, decimals=6), np.ones_like(rounded_adc_timings), phase

        sampling_idx = np.searchsorted(time_raster, rounded_adc_timings, side="left")
        idx_not_on_raster = np.logical_not(np.isclose(time_raster[sampling_idx],
                                                      rounded_adc_timings, atol=1e-6))
        sampling_idx_left_shift = sampling_idx[idx_not_on_raster] - 1

        if force_raster:
            augmented_idx = np.sort(np.concatenate([np.squeeze(sampling_idx),
                                                    sampling_idx_left_shift]))
            unique_sampling_indice = np.unique(augmented_idx, return_counts=False,
                                               return_index=False, return_inverse=False)
            adc_on = np.zeros_like(time_raster)
            adc_on[unique_sampling_indice] = 1
            phase = np.insert(phase, np.where(idx_not_on_raster)[0] + 1, phase[idx_not_on_raster])
        else:
            time_raster = np.insert(time_raster, sampling_idx[idx_not_on_raster],
                                    rounded_adc_timings[idx_not_on_raster])
            adc_on = np.zeros_like(time_raster)
            adc_on[np.searchsorted(time_raster, rounded_adc_timings, side="left")] = 1

        return np.around(time_raster, decimals=6), adc_on, phase

    # pylint: disable=R0914, C0103
    def calculate_kspace(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """ Evaluates the k-space trajectory of the sequence.

        **Note**: All RF-pulses with a smaller flip-angle other than 180° are assumed to be
        excitation pulses. 180° - Refocusing pulses result in a complex conjugation of the
        trajectory. Consecutive excitation pulses are handled by starting from k-space center again.

        :return: Tuple of arrays containing:

                - k-space trajectory on gradient rasters (-1, 3) in 1/m
                - k-space points at adc events (-1, 3) in 1/m
                - time at adc events (-1 ) in ms
        """
        # Subdivide gradient waveforms in periods between rf events for integration
        rf_events = [block.rf_events for block in self._blocks if isinstance(block, RFPulse)]

        if rf_events:
            rf_factors = []
            for (t, fa) in rf_events:
                factor = -1. if np.isclose(fa, np.pi, rtol=np.pi / 50) else 0.
                rf_factors.append([t.m_as("ms"), factor])
            rf_factors = np.stack(rf_factors)
            rf_factors = rf_factors[np.argsort(rf_factors[:, 0])]
        else:
            rf_factors = None

        t_grid_global, gradient_waveform = self.gradients_to_grid()
        k_of_t = np.zeros([3, gradient_waveform.shape[1]])

        if rf_factors is not None:
            rf_event_tidx = np.searchsorted(np.round(t_grid_global,decimals=6), np.round(rf_factors[:, 0],decimals=6))
            rf_event_tidx = np.concatenate([rf_event_tidx, [-1, ]])
            for idx, factor in enumerate(rf_factors[:, 1]):
                start, end = rf_event_tidx[idx:idx + 2]
                dt = np.diff(t_grid_global[start:end]).reshape(1, -1)
                wf = gradient_waveform[:, start:end]
                delta_k = np.cumsum(dt * (wf[:, 1:] + wf[:, 0:-1]) / 2, axis=1)
                delta_k *= self._system_specs.gamma.m_as("MHz/T")  # 1/mT/ms
                k_of_t[:, start + 1:end] = factor * k_of_t[:, start - 1:start] + delta_k
        else:
            k_of_t[:, 1:] = np.cumsum(np.diff(t_grid_global).reshape(1, -1) *
                                      (gradient_waveform[:, 1:] + gradient_waveform[:, :-1]) / 2,
                                      axis=1) * self._system_specs.gamma.m_as("MHz/T")

        # Evaluate k-space position at adc-events
        all_adc_timings = [block.adc_timing.m_as("ms") for block in self._blocks
                           if isinstance(block, ADC)]
        if all_adc_timings:
            t_adc = np.around(np.concatenate(all_adc_timings, axis=0), decimals=6)
            k_adc = np.stack([np.interp(t_adc, t_grid_global, k) for k in k_of_t])
        else:
            k_adc = None
            t_adc = None

        return k_of_t, k_adc, t_adc

    # pylint: disable=R0914, C0103
    def calculate_moment(self, moment: int = 0, center_time: Quantity = Quantity(0., "ms"),
                         end_time: Quantity = None, start_time: Quantity = None) -> Quantity:
        """ Calculates gradient moments about a given center point

        :param moment: int of desired moment number
        :param center_time: Quantity of center time to calculate moment about, defaults to t=0
        :param end_time: Time to calculate moment up to, default is end of sequence
        :param start_time: Time to calculate moment from, default is start of sequence
        :return: Quantity [Mx, My, Mz]
        """

        # Get all gradient break points
        t, g = self.combined_gradients()

        if t is None or g is None:
            return Quantity([0., 0., 0.], 'mT/m*ms**' + str(moment + 1))

        if start_time is None:
            tstart = t[0]
        else:
            tstart = start_time.m_as("ms")
        
        if end_time is None:
            tend = t[-1]
        else:
            tend = end_time.m_as("ms")

        tcur = t
        gcur = g

        # If the start and end time are outside the range of the gradient definition
        # the gradient definition is cut to the range of the start and end time
        if tend<t[-1]:
            ind_end = np.argwhere(t>=tend)[0][0]
            tcur = tcur[:ind_end]
            gcur = gcur[:,:ind_end]

        if tstart>t[0]:
            ind_start = np.argwhere(t>=tstart)[0][0]
            tcur = tcur[ind_start:]
            gcur = gcur[:,ind_start:]

        # Interpolate the gradient definition to the start and end time
        if tstart>t[0]:
            gintstart = g[:,ind_start-1] + (g[:,ind_start]-g[:,ind_start-1])/(t[ind_start]-t[ind_start-1])*(tstart-t[ind_start-1])
            gcur = np.insert(gcur,0,gintstart,axis=1)
            tcur = np.insert(tcur,0,tstart)

        if tend<t[-1]:
            gintend = g[:,ind_end-1] +(g[:,ind_end]-g[:,ind_end-1])/(t[ind_end]-t[ind_end-1])*(tend-t[ind_end-1])
            gcur = np.append(gcur,gintend[:,np.newaxis],axis=1)
            tcur = np.append(tcur,tend)

        # Set center time
        tcur = tcur - center_time.m_as("ms")

        # Back to the original units
        t1 = Quantity(tcur[:-1],'ms')
        t2 = Quantity(tcur[1:],'ms')
        G1 = Quantity(gcur[:,:-1],'mT/m')
        G2 = Quantity(gcur[:,1:],'mT/m')

        # Use solution for arbitrary linear section, to nth order
        result = (G2-G1)*(t1**(moment+2) - t2**(moment+2))/((moment+2)*(t1-t2)) + (G1*t2-G2*t1)*(t1**(moment+1) - t2**(moment+1))/((moment+1)*(t1-t2))
        result = result.sum(axis=1)

        return result
