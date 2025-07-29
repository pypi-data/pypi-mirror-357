__all__ = ["PulseSeqFile"]

from typing import Tuple, List, Iterable, Any
import os
import sys
import re
from collections import OrderedDict, deque
from types import SimpleNamespace
import hashlib

import numpy as np
from pint import Quantity
from tqdm import tqdm

import cmrseq
from cmrseq import bausteine
from cmrseq import SystemSpec, Sequence


class PulseSeqFile:
    """ API for reading and writing Pulseq definition files"""
    #: Tuple of strings defining the Semantic delimiters of the file
    # Definitions, Extensions, signature
    SECTION_HEADERS: Tuple[str, ...] = ("[VERSION]", "[DEFINITIONS]", "[BLOCKS]",
                                        "[GRADIENTS]", "[RF]", "[TRAP]", "[ADC]",
                                        "[EXTENSIONS]", "[SHAPES]", "[SIGNATURE]")
    #: Required definitions in [DEFINITIONS] - section
    REQUIRED_DEFINITIONS: Tuple[str, ...] = ("AdcRasterTime", "BlockDurationRaster",
                                             "GradientRasterTime", "RadiofrequencyRasterTime")

    #: Assembled python like version number
    version: str
    #: Dictionary containing Quantities[Time] for 'grad', 'rf', 'adc' and 'block' raster time
    raster_times: dict
    #: Dictionary containing values specified in the [DEFINITIONS] section
    additional_defs: dict
    #: Integer array (n_blocks, 8) containing the Block-definitions
    block_array: np.ndarray
    #: Dictionary (id: shape) containing the uncompressed shape definitions
    shape_table: OrderedDict
    #: Dictionary containing the RF definitions per shape_id as dictionary with following keys:
    #: dict_keys=(phase_offset, frequency_offset, delay,
    #             shape_ids=[mag, phase, time], amplitude)
    rf_table: OrderedDict
    #: Dictionary containing the ADC definition per shape_id as dictionary with following keys:
    #: dict_keys=(num_samples, dwell, delay, frequency_offset, phase_offset)
    adc_table: OrderedDict
    #: Dictionary containing the trapezoidal gradient definitions per shape_id as dictionary
    #  with following keys: dict_keys=(amplitude, rise_time, flat_duration, fall_time, delay)
    traps_table: OrderedDict
    #: Dictionary containing the shape-gradient definitions per shape_id as dictionary
    #: dict_keys=(delay, shape_ids=[amp, time], amplitude)
    grads_table: OrderedDict
    #: Dictionary containing the extensions definiton
    ext_table: OrderedDict

    def __init__(self, file_path: str = None, sequence: Sequence = None):
        if (file_path is not None and sequence is not None) or \
                (file_path is None and sequence is None):
            raise ValueError("Exactly one of the input sources must be specified.")

        self.shape_table = OrderedDict()  # hash_val: (id, n_samples, 1d-arr)
        self.shape_hash_table = OrderedDict()
        self.rf_table = OrderedDict()  # hash_val: (id, amp, mag_id, phs_id, time_id, delay, freq, phase)
        self.rf_hash_table = OrderedDict()
        self.traps_table = OrderedDict()
        self.traps_hash_table = OrderedDict()
        self.grads_table = OrderedDict()
        self.grads_hash_table = OrderedDict()
        self.adc_table = OrderedDict()
        self.adc_hash_table = OrderedDict()
        self.ext_table = OrderedDict()

        if file_path is not None:
            self.from_pulseq_file(file_path)
        elif sequence is not None:
            self.from_sequence(sequence)

    def from_pulseq_file(self, filepath: str):
        """ Loads a *.seq file and parses all sections into the

        :raise: ValueError if file does not exist
        :param filepath: path to a file of type *.seq
        """

        if not os.path.exists(filepath):
            raise ValueError(f"No pulseq file found at specified location:\n\t{filepath}")

        with open(filepath, "r") as seqfile:
            all_lines = seqfile.read().splitlines()
        all_lines = [re.sub(r'\s+', ' ', line.strip()) for line in all_lines]

        # Find section starts and calculate number of lines per section
        sections = self._subdivide_sections(all_lines)

        # Parse Meta information (version and definitions)
        self.version = self._parse_version(sections["[VERSION]"])
        self.raster_times, self.additional_defs = self._parse_definitions(sections["[DEFINITIONS]"])

        # Parse block definitions
        self.block_array = np.genfromtxt(sections["[BLOCKS]"], comments="#",
                                         delimiter=" ", dtype=int)

        # Parse lookup tables for block definitions
        shape_table, rf_table, adc_table, traps_table, grads_table, ext_table = [{} for _ in
                                                                                 range(6)]
        if "[SHAPES]" in sections.keys():
            shape_table = self._parse_shapes(sections["[SHAPES]"])
        self.shape_table = shape_table

        if "[RF]" in sections.keys():
            # If any RF is specified, SHAPES must be present in definitons as well
            rf_table = self._parse_rf(sections["[RF]"])
        self.rf_table = rf_table

        if "[ADC]" in sections.keys():
            adc_table = self._parse_adc(sections["[ADC]"])
        self.adc_table = adc_table

        if "[TRAP]" in sections.keys():
            traps_table = self._parse_traps(sections["[TRAP]"])
        self.traps_table = traps_table

        if "[GRADIENTS]" in sections.keys():
            grads_table = self._parse_gradients(sections["[GRADIENTS]"])
        self.grads_table = grads_table

        if "[EXTENSIONS]" in sections.keys():
            print(2)
        self.ext_table = ext_table

    @staticmethod
    def _subdivide_sections(all_lines) -> OrderedDict:
        """ Parses the file for the pre-defined sections and divides the lines according
         to captions. Lines per section is returned in a dictionary whose keys are the actually
         provided section headers.

        :param all_lines: List[str]
        :return: OrderedDict(section_header=List[str])
        """
        # Find line-indices that match the section headers
        section_starts = OrderedDict((line.strip(), line_idx + 1)
                                     for line_idx, line in enumerate(all_lines)
                                     if line.strip() in PulseSeqFile.SECTION_HEADERS)

        # Roll the indices of the actually specified sections to define the end-of-section lines
        provided_sections = list(section_starts.keys())
        section_ends = {k: section_starts[k_next] - 1 for k_next, k
                        in zip(provided_sections[1:], provided_sections[:-1])}
        section_ends[PulseSeqFile.SECTION_HEADERS[-1]] = len(all_lines)

        # Index the given lines according to sections and store them in a dictionary
        sections_dict = OrderedDict([(k, all_lines[section_starts[k]:section_ends[k]])
                                     for k in provided_sections])
        return sections_dict

    @staticmethod
    def _parse_version(version_lines: List[str]) -> str:
        """ Converts the following lines to a major.minor.revision version number:

        .. code-block::

            [VERSION]
            major X
            minor Y
            revision z

        :param version_lines: List[str]
        :return: str
        """
        cleaned_lines = [v.strip() for v in version_lines if (len(v) > 0 and v[0] != "#")]
        version_str = "".join(cleaned_lines).replace("major ", "").replace("minor ", ".")
        return version_str.replace("revision ", ".")

    @staticmethod
    def _parse_definitions(definition_lines: List[str]) -> (dict, dict):
        """ Converts the following lines to two dictionaries (required, optional):

        .. code-block::

            [DEFINITIONS]
            AdcRasterTime float                         (required)
            BlockDurationRaster float                   (required)
            GradientRasterTime float                    (required)
            RadiofrequencyRasterTime float              (required)
            AdditionalProperty any                      (optional)
            ...

        :raises: ValueError if the definition does not contain all of the required properties

        :param definition_lines: List[str]
        :return: dict, dict -> required_properties, addition_properties
        """
        definition_lines = [line.strip() for line in definition_lines
                            if (len(line) > 0 and line[0] != "#")]
        definitions = {l.split()[0]: l.split()[1] for l in definition_lines}
        if not all([k in definitions.keys() for k in PulseSeqFile.REQUIRED_DEFINITIONS]):
            raise ValueError("Given definition section does not contain all required values:\n"
                             f"\tGot: {definitions.keys()}\n"
                             f"\tExpected: {PulseSeqFile.REQUIRED_DEFINITIONS}")
        raster_times = dict(
            grad=Quantity(float(definitions["GradientRasterTime"]), "s"),
            rf=Quantity(float(definitions["RadiofrequencyRasterTime"]), "s"),
            adc=Quantity(float(definitions["AdcRasterTime"]), "s"),
            blocks=Quantity(float(definitions["BlockDurationRaster"]), "s")
        )
        [definitions.pop(k) for k in PulseSeqFile.REQUIRED_DEFINITIONS]
        additional_definitions = definitions
        return raster_times, additional_definitions

    @staticmethod
    def _parse_rf(rf_lines: List[str]) -> dict:
        """ Parses the RF definitions given in following format

        .. code-block::

            # Format of RF events:
            # id amplitude mag_id phase_id time_shape_id delay freq phase
            # ..        Hz   ....     ....          ....    us   Hz   rad
            [RF]
            1         2500 1 2 3 100 0 0
            ...

        :param rf_lines: List[str] starting from the first line after [RF]
        :return: dict(rf_id = dict([time_points, waveform, phase_offset, frequency_offset, delay]))
        """
        rf_lines = [line.strip() for line in rf_lines if (len(line) > 0 and line[0] != "#")]
        rf_defs = []
        for line in rf_lines:
            line = np.genfromtxt([line, ], delimiter=" ")
            id_ = int(line[0])
            amplitude_scaling = Quantity(float(line[1]), "Hz")
            delay = Quantity(float(line[5]), "us")
            frequency_offset = Quantity(line[6], "Hz")
            phase_offset = Quantity(line[7], "rad")
            rf_defs.append((id_, dict(phase_offset=phase_offset, frequency_offset=frequency_offset,
                                      delay=delay, shape_ids=[int(line[i]) for i in (2, 3, 4)],
                                      amplitude=amplitude_scaling)))

        return OrderedDict(rf_defs)

    @staticmethod
    def _parse_gradients(gradient_lines: List[str]) -> dict:
        """  Parses the arbitrary gradient definitions given in following format

        .. code-block::

            # Format of arbitrary gradients:
            #   time_shape_id of 0 means default timing (stepping with grad_raster starting
            #     at 1/2 of grad_raster)
            # id amplitude amp_shape_id time_shape_id delay
            # ..      Hz/m       ..         ..          us
            [GRADIENTS]
            1 -1.10938e+06 3 4 230
            2  1.10938e+06 5 6 0
            ...


        :param gradient_lines:
        :return:
        """
        gradient_lines = [line.strip() for line in gradient_lines
                          if (len(line) > 0 and line[0] != "#")]

        grad_defs = []
        for line in gradient_lines:
            line = np.genfromtxt([line, ], delimiter=" ", dtype=np.float64, comments="#")
            id_ = int(line[0])
            amplitude_scaling = Quantity(line[1], "Hz/m")
            amp_shape_id, time_shape_id = int(line[2]), int(line[3])
            delay = Quantity(line[4], "us")
            grad_defs.append((id_, dict(delay=delay, shape_ids=[amp_shape_id, time_shape_id],
                                        amplitude=amplitude_scaling)))
        return OrderedDict(grad_defs)

    @staticmethod
    def _parse_traps(trap_lines: List[str]):
        """ Parses trapezoidal gradient definitions

        .. code-block::

            # Format of trapezoid gradients:
            # id amplitude rise flat fall delay
            # ..      Hz/m   us   us   us    us
            [TRAP]
             4 -1.09777e+06 190  340 190   0
             5  1.09777e+06 190  340 190   0
             7 -1.06902e+06 180  360 180   0

        :param trap_lines: List[str] starting from the first line after [TRAP]
        :return:
        """
        trap_lines = [line.strip() for line in trap_lines if (len(line) > 0 and line[0] != "#")]
        trap_defs = []
        for line in trap_lines:
            line = np.genfromtxt([line, ], delimiter=" ")
            trap_defs.append((int(line[0]),
                              dict(amplitude=Quantity(float(line[1]), "Hz/m"),
                                   rise_time=Quantity(float(line[2]), "us"),
                                   flat_duration=Quantity(float(line[3]), "us"),
                                   fall_time=Quantity(float(line[4]), "us"),
                                   delay=Quantity(float(line[5]), "us"))
                              ))
        return OrderedDict(trap_defs)

    @staticmethod
    def _parse_adc(adc_lines: List[str]) -> dict:
        """ Parses the ADC definitions given in following format

            .. code-block::

                # Format of ADC events:
                # id num dwell delay freq phase
                # ..  ..    ns    us   Hz   rad
                [ADC]
                1 256 10000 740 0 3.14159
                2 256 10000 740 0 0

            :param adc_lines: List[str] starting from the first line after [RF]
            :return: dict(rf_id=dict([num dwell delay freq phase]))
        """
        adc_lines = [line.strip() for line in adc_lines if (len(line) > 0 and line[0] != "#")]
        adc_defs = []
        for line in adc_lines:
            line = np.genfromtxt([line, ], delimiter=" ")
            id_ = int(line[0])
            adc_defs.append((id_, dict(num_samples=int(line[1]),
                                       dwell=Quantity(float(line[2]), "ns"),
                                       delay=Quantity(float(line[3]), "us"),
                                       frequency_offset=Quantity(line[4], "Hz"),
                                       phase_offset=Quantity(line[5], "rad")))
                            )
        return OrderedDict(adc_defs)

    @staticmethod
    def _parse_shapes(shape_lines: List[str]) -> dict:
        """ Parses shapes stored in following format:

        .. code-block::
            [SHAPES]

            shape_id 1
            num_samples N2
            ...  (compressed samples)

            ...

        Specification of the compression format can be found at:
        https://pulseq.github.io/specification.pdf

        :raises: AssertionError if num_samples mismatches the actually provided number of samples

        :param shape_lines: List[str]
        :return: dict(shape_id=np.array) dictionary of uncompressed shapes
        """
        header_lines = [idx for idx, line in enumerate(shape_lines) if "shape_id" in line] + [-1]
        shapes = {}
        for hidx, hidx_next in zip(header_lines[0:-1], header_lines[1:]):
            id_ = int(re.findall(r'\d+', shape_lines[hidx])[0])
            n_samples = int(re.findall(r'\d+', shape_lines[hidx + 1])[0])
            shape_arr = np.atleast_1d(np.genfromtxt(shape_lines[hidx + 2:hidx_next]))
            if n_samples > shape_arr.shape[0]:
                shape_arr = PulseSeqFile._decompress_shape(shape_arr)
                assert shape_arr.shape[0] == n_samples

            shapes.update({id_: shape_arr})
        return shapes

    @staticmethod
    def _decompress_shape(shape_arr: np.ndarray):
        """Inverts pseudo run-length encoding of shape definitions
        From definition:

            When used as amplitude shapes for gradient or RF objects, the decompressed
            samples must be in the normalised range of [-1, 1] (e.g. the absolute value of
            the shape must be normalized to the range of [0  1]). Since the purpose of this
            section is to define the basic shape of a gradient or RF pulse, the amplitude
            information is defined in the events section. This allows the same shape to be
            used with different amplitudes, without repeated definitions.
            The number of points after decompressing all samples defined in a shape must
            equal the number declared in num_samples.

        :param shape_arr:
        :return:
        """
        expansion_points = np.where(shape_arr > 1)
        expansion_factors = shape_arr[expansion_points].astype(int)
        repeating_value = shape_arr[(expansion_points[0] - 1,)]
        insertion_indices = np.concatenate([np.zeros(f) + p for f, p
                                            in zip(expansion_factors, expansion_points[0])], axis=0)
        insertion_values = np.concatenate([np.zeros(f) * v for f, v
                                           in zip(expansion_factors, repeating_value)], axis=0)
        shape_arr = np.insert(shape_arr, insertion_indices.astype(int), insertion_values)
        shape_arr = shape_arr[np.where(np.abs(shape_arr) <= 1)]
        out = np.empty(shape_arr.shape, dtype=np.float64)
        np.cumsum(shape_arr, out=out)
        out[0] = shape_arr[0]
        return out

    def write(self, filepath: str):
        """

        :raises: ValueError if file at specified location already exists

        :param filepath:
        :return: None
        """
        # if os.path.exists(filepath):
        #     raise ValueError("File at specified location already exists")

        version_sec = self._format_version(self.version)
        definition_sec = self._format_definitions(self.raster_times, self.additional_defs)
        block_sec = self._format_blocks_def(self.block_array)
        rf_sec = self._format_rf(self.rf_table)
        grad_sec = self._format_gradients(self.grads_table)
        trap_sec = self._format_traps(self.traps_table)
        adc_sec = self._format_adc(self.adc_table)
        shape_sec = self._format_shapes(self.shape_table)

        total = "\n".join([version_sec, definition_sec, block_sec, rf_sec,
                           grad_sec, trap_sec, adc_sec, shape_sec])

        total = self._sign_definition(total)

        with open(filepath, "w+") as wfile:
            wfile.write(total)

    @staticmethod
    def _format_version(version_str: str) -> str:
        major, minor, revision = version_str.split(".")
        try:
            version = cmrseq.__version__
        except AttributeError:
            version = "0.0"

        return_string = "#Pulseq sequence file\n#Exported from python package " \
                        f"cmrseq {version}\n\n[VERSION]\n"
        return return_string + f"major {major}\nminor {minor}\nrevision {revision}\n"

    @staticmethod
    def _format_definitions(raster_times: dict, additional_info: dict) -> str:
        return_string = "[DEFINITIONS]\n" + \
                        f"AdcRasterTime {raster_times['adc'].m_as('s')}\n" + \
                        f"BlockDurationRaster {raster_times['blocks'].m_as('s')}\n" + \
                        f"GradientRasterTime {raster_times['grad'].m_as('s')}\n" + \
                        f"RadiofrequencyRasterTime {raster_times['rf'].m_as('s')}\n"
        return_string += "\n".join([f"{k} {v}" for k, v in additional_info.items()])
        return return_string + "\n"

    @staticmethod
    def _format_blocks_def(block_array: np.ndarray) -> str:
        header = "# Format of blocks:\n"
        header += " ".join(
            [f"{s:<6}" for s in ("# NUM", "DUR", "RF", "GX", "GY", "GZ", "ADC", "EXT")])
        header += "\n[BLOCKS]\n"
        arr_string = "\n".join([np.array2string(row, prefix="", separator=" ",
                                                formatter={'int': lambda x: f"{x:<6}"})[
                                1:-1].strip()
                                for row in block_array])
        return header + arr_string + "\n"

    @staticmethod
    def _format_rf(rf_table) -> str:
        return_string = (# Format of RF events:\n"
                         f"# {'id':<3} {'amplitude':<13} {'mag_id':<6} {'phase_id':<8}"
                         f" {'time_shape_id':<13} {'delay':<7} {'freq':<7} {'phase':<6}\n")
        return_string += f"# {'..':<3} {'Hz':<13} {'..':<6} {'..':<8} " \
                         f"{'..':<13} {'us':<7} {'Hz':<7} {'rad':<6}\n[RF]\n"
        for id_, rfdef in rf_table.items():
            peak_amp = float(rfdef["amplitude"].m_as("Hz"))
            delay = np.around(rfdef["delay"].m_as("us"), decimals=0).astype(int)
            phase = rfdef["phase_offset"].m_as("rad")
            freq = rfdef["frequency_offset"].m_as("Hz")
            mag_id, phase_id, t_id = rfdef["shape_ids"]
            line = f"{id_:<5} {peak_amp:<13.5e} {mag_id:<5} {phase_id:<5} {t_id:<5}" \
                   f" {delay:<7} {freq:<7} {phase:1.6f}\n"
            return_string += line
        return return_string

    @staticmethod
    def _format_gradients(grad_table) -> str:
        return_string = ("# Format of arbitrary gradients:\n#   time_shape_id of 0 means default"
                         " timing (stepping with grad_raster starting at 1/2 of grad_raster)\n"
                         f"# {'id':<3} {'amplitude':<13} {'amp_shape_id':<12} {'time_shape_id':<13}"
                         f" {'delay':<7}\n"
                         f"# {'..':<3} {'Hz':<13} {'..':<12} {'..':<13} {'us':<7}\n[GRADIENTS]\n")
        for id_, gdef in grad_table.items():
            peak_amp = float(gdef["amplitude"].m_as("Hz/m"))
            delay = np.around(gdef["delay"].m_as("us"), decimals=0).astype(int)
            mag_id, t_id = gdef["shape_ids"]
            line = f"{id_:<5} {f'{peak_amp:<13.5e}':<13} {mag_id:<12} {t_id:<13} {delay:<7}\n"
            return_string += line
        return return_string

    @staticmethod
    def _format_traps(traps_table) -> str:
        return_string = "# Format of trapezoid gradients:\n# id amplitude rise flat fall delay\n"
        return_string += f"# {'..':<3} {'Hz/m':<13} {'us':<7} {'us':<7} {'us':<7} {'us':<7}\n[TRAP]\n"
        for id_, tdef in traps_table.items():
            peak_amp = float(tdef["amplitude"].m_as("Hz/m"))
            rise, flat, fall, delay = [np.around(tdef[k].m_as("us"), decimals=0).astype(int) for
                                       k in ("rise_time", "flat_duration", "fall_time", "delay")]
            line = f"{id_:<5} {f'{peak_amp:<13.5e}':<13} {rise:<7} {flat:<7} {fall:<7} {delay:<7}\n"
            return_string += line
        return_string += "\n"
        return return_string

    @staticmethod
    def _format_adc(adc_table) -> str:
        return_string = (f"# Format of ADC events::\n# {'id':<3} {'num':<6} {'dwell':<9}"
                         f" {'delay':<6} {'freq':<13} {'phase':<6}\n")
        return_string += f"# {'..':<3} {'..':<6} {'ns':<9} {'us':<6} {'Hz/m':<13} {'rad':<6}\n[ADC]\n"
        for id_, adcdef in adc_table.items():
            num = adcdef['num_samples']
            dwell = np.round(adcdef['dwell'].m_as("ns"), decimals=0).astype(int)
            if not np.isclose(dwell, adcdef['dwell'].m_as("ns"), atol=6):
                raise ValueError(f"Encountered invalid adc dwell not on integer ns {adcdef}")
            delay = np.round(adcdef['delay'].m_as("us"), decimals=0).astype(int)
            if not np.isclose(delay, adcdef['delay'].m_as("us"), atol=6):
                raise ValueError(f"Encountered invalid adc delay not on integer us {adcdef}")
            freq = adcdef['frequency_offset'].m_as("Hz")
            phase = adcdef['phase_offset'].m_as("rad")
            line = f"{id_:<5} {num:<6} {dwell:<9} {delay:<6} {f'{freq:<13.5e}':<13} {phase:<5}\n"
            return_string += line
        return return_string

    @staticmethod
    def _format_shapes(shape_table: dict) -> str:
        return_string = "# Sequence Shapes\n[SHAPES]\n\n"
        for shape_id, shape_arr in shape_table.items():
            return_string += f"shape_id {shape_id}\nnum_samples {shape_arr.shape[0]}\n"
            if np.max(np.abs(shape_arr)) <= 1:
                compressed_shape = PulseSeqFile._compress_shape(np.around(shape_arr, decimals=12))
            else:
                compressed_shape = shape_arr
            arr_str = np.array2string(compressed_shape, separator="\n",
                                      floatmode="maxprec_equal", threshold=int(1e5))[1:-1]
            return_string += arr_str.replace(" ", "").replace(" ", "").replace(" ", "")
            return_string += "\n\n"
        return return_string

    @staticmethod
    def _compress_shape(shape_arr) -> np.ndarray:
        """ Pseudo run-length encoding algorithm, compressing MR-shape definitions according to the
        PulseSeq format (https://pulseq.github.io/specification.pdf).

        This code is directly adapted from the pypulseq implementation at:
        https://github.com/imr-framework/pypulseq/blob/dev/pypulseq/compress_shape.py

        Algorithm:

        .. code-block::

            1. compute derivative
            2. find consecutively at least 4 times reoccuring values
            3. replace re-occuring values from 3rd position on by the number of occurences

        :param shape_arr: 1D np.darray
        :param force_compression: if true applies compression even if the number of samples is not
                                    smaller
        :return:
        """
        if len(shape_arr) <= 4:  # Avoid compressing very short shapes
            return shape_arr

        # Single precision floating point has ~7.25 decimal places
        quant_factor = 1e-7
        decompressed_shape_scaled = shape_arr / quant_factor
        datq = np.round(
            np.concatenate((decompressed_shape_scaled[[0]], np.diff(decompressed_shape_scaled)))
        )
        qerr = decompressed_shape_scaled - np.cumsum(datq)
        qcor = np.concatenate(([0], np.diff(np.round(qerr))))
        datd = datq + qcor

        # RLE of datd
        starts = np.concatenate(([0], np.flatnonzero(datd[1:] != datd[:-1]) + 1))
        lengths = np.diff(np.concatenate((starts, [len(datd)])))
        values = datd[starts] * quant_factor

        # Repeat values of any run-length>1 three times: (value, value, length)
        rl_gt1 = lengths > 1
        repeats = 1 + rl_gt1 * 2
        v = np.repeat(values, repeats)

        # Calculate indices of length elements and insert length values
        inds = np.cumsum(repeats) - 1
        v[inds[rl_gt1]] = lengths[rl_gt1] - 2

        # Decide whether compression makes sense, otherwise store the original
        if len(shape_arr) > len(v):
            return v
        else:
            return shape_arr

    @staticmethod
    def _sign_definition(total: str):
        string_hash = hashlib.md5(total.encode('utf-8')).hexdigest()
        template = ("\n[SIGNATURE]\n# This is the hash of the Pulseq file, calculated right" 
                   " before the [SIGNATURE] section was added\n# It can be reproduced/verified" 
                   " with md5sum if the file trimmed to the position right above [SIGNATURE]\n#" 
                   " The new line character preceding [SIGNATURE] BELONGS to the signature " 
                   "(and needs to be sripped away for recalculating/verification)\n")
        template += f"Type md5\nHash {string_hash}"
        return total + template

    def to_cmrseq(self, system_specs: SystemSpec, block_indices: Iterable[int] = None) -> List[
        Sequence]:
        """ Converts the parsed file into a list of cmrseq.Sequence objects.

        :param gyromagentic_ratio: in MHz/T
        :param max_slew: in mT/m
        :param max_grad: in mT/m/ms
        :param block_indices: Iterable[int] specifiying which blocks to convert if None all blocks
                                are converted
        :return: List of cmrseq.Sequence each representing one block of the pulseseq definition
        """
        if block_indices is None:
            block_indices = range(self.block_array.shape[0])

        sequence_objects = []
        # Assumption: each block can contain one each of the classes (RF, GX, GY, GZ, ADC, EXT)
        for idx in tqdm(block_indices, desc="Converting block definitons to CMRseq objects"):
            sequence_blocks = []
            block_def = self.block_array[idx]

            # Construct RF
            rf_def = self.rf_table.get(block_def[2], None)
            if rf_def is not None:
                rf_object = self._rfdef_to_block(rf_def, system_specs, name=f"rf_id_{block_def[2]}")
                sequence_blocks.append(rf_object)

            # Construct Gradients
            gradients_per_dir = self._graddef_to_block(block_def, system_specs)
            sequence_blocks.extend(gradients_per_dir)

            # Construct ADC
            adc_def = self.adc_table.get(block_def[6], None)
            if adc_def is not None:
                adc_object = bausteine.SymmetricADC(system_specs=system_specs,
                                                    **adc_def)
                sequence_blocks.append(adc_object)

            # Only block duration is specified --> Delay
            if len(sequence_blocks) == 0:
                sequence_blocks.append(bausteine.Delay(system_specs=system_specs,
                                                       duration=float(block_def[1]) *
                                                                self.raster_times["blocks"]))

            # Pulseq files can add a delay by specifying a block duration that is longer
            # than all contained events. In this case a padding with a delay is necessary
            target_block_dur = block_def[1] * self.raster_times["blocks"].to("ms")
            max_block_dur = Quantity(max([b.tmax.m_as("ms") for b in sequence_blocks]), "ms")
            if target_block_dur.m_as("ms") - max_block_dur.m_as("ms") > 1e-6:
                sequence_blocks.append(bausteine.Delay(system_specs=system_specs,
                                                       duration=target_block_dur - max_block_dur,
                                                       delay=max_block_dur))

            sequence_objects.append(Sequence(sequence_blocks, system_specs=system_specs))
        return sequence_objects

    def _rfdef_to_block(self, rf_def: dict, system_specs: SystemSpec,
                        name: str) -> 'bausteine.RFPulse':
        """ Converts a Pulseq definition of a RF pulse to a cmrseq RFPulse object

        :param grad_def:
                Expected dictionary keys:
                    - phase_offset  (rad)
                    - frequency_offset (Hz)
                    - delay (us)
                    - shape_ids ()
                    - amplitude (Hz)
        :return: ArbitraryRFPulse
        """
        mag_id, phase_id, time_id = rf_def["shape_ids"]
        normed_magnitude = self.shape_table[mag_id]
        phase_shape = Quantity(self.shape_table[phase_id] * np.pi * 2, "rad")
        amplitude_scaling = (rf_def["amplitude"] / system_specs.gamma.to("Hz/uT")).to("uT")

        if time_id == 0:
            # if no shape is specified (id==0), raster time is assumed where RF shapes are
            # gridded with half a raster-time shift in pulseq-definition
            # to make it compatible with cmrseq interpolation to the on-raster points is performed
            n_samples = normed_magnitude.shape[0]
            time_shape_shifted = (np.arange(0, n_samples, 1) + 0.5)
            time_shape_shifted *= self.raster_times["rf"]
            time_shape = np.arange(0, n_samples + 1, 1) * self.raster_times["rf"]
            phase_shape = Quantity(np.interp(time_shape, time_shape_shifted,
                                             phase_shape.m_as("rad"), left=0, right=0), "rad")
            normed_magnitude = np.interp(time_shape, time_shape_shifted, normed_magnitude,
                                         left=0, right=0)
        else:
            time_shape = self.shape_table[time_id] * self.raster_times["rf"]

        waveform = normed_magnitude * amplitude_scaling * np.exp(1j * phase_shape)
        delay, foffset, poffset = [rf_def[k] for k in ("delay", "frequency_offset", "phase_offset")]
        rf = bausteine.ArbitraryRFPulse(system_specs, time_points=time_shape,
                                        waveform=waveform, delay=delay, frequency_offset=foffset,
                                        phase_offset=poffset, snap_to_raster=False, name=name)
        return rf

    def _graddef_to_block(self, block_def: dict, system_specs: SystemSpec) -> \
            List['bausteine.Gradient']:
        """
        :param block_def: (id, duration, rf, gx, gy, gz, adc, ext)
        :param system_specs:
        :return:
        """
        gradient_blocks = []
        for dir_idx, direction in zip([3, 4, 5], np.eye(3, 3)):
            # Check if index belongs to a trapezoidal, otherwise construct arbitrary
            if block_def[dir_idx] != 0:
                g_def = self.traps_table.get(block_def[dir_idx], None)
                if g_def is not None:
                    amplitude = (g_def["amplitude"] / system_specs.gamma.to("Hz/mT")).to("mT/m")
                    gradient_object = bausteine.TrapezoidalGradient(
                                                    system_specs,
                                                    amplitude=amplitude,
                                                    rise_time=g_def["rise_time"],
                                                    flat_duration=g_def["flat_duration"],
                                                    fall_time=g_def["fall_time"],
                                                    delay=g_def["delay"],
                                                    orientation=direction,
                                                    name=f"trapezoidal_id{block_def[dir_idx]}",
                                                    snap_to_raster=False)
                else:
                    g_def = self.grads_table.get(block_def[dir_idx], None)
                    amp_shape_id, time_shape_id = g_def["shape_ids"]
                    amplitude_scaling = (g_def["amplitude"] / system_specs.gamma.to("Hz/mT"))
                    waveform = self.shape_table[amp_shape_id] * amplitude_scaling.to("mT/m")

                    if time_shape_id == 0:
                        # if no shape is specified (id==0), raster time is assumed where arbitrary
                        # gradient shapes are gridded with half a raster-time shift in
                        # pulseq-definition. This must be reverted for cmrseq definitions
                        time_points_shifted = (np.arange(0, waveform.shape[0]) + 0.5
                                               * self.raster_times["grad"])
                        time_shape = (np.arange(0, n_samples + 1, 1)
                                      * self.raster_times["rf"])
                        waveform = np.interp(time_shape, time_points_shifted, waveform)
                    else:
                        time_points = self.shape_table[time_shape_id] * self.raster_times["grad"]

                    waveform = waveform[np.newaxis] * direction[:, np.newaxis]
                    gradient_object = bausteine.ArbitraryGradient(
                                                system_specs=system_specs,
                                                waveform=waveform,
                                                time_points=time_points,
                                                delay=g_def["delay"],
                                                name=f"shape_gradient_id{block_def[dir_idx]}",
                                                snap_to_raster=False)
                gradient_blocks.append(gradient_object)
        return gradient_blocks

    def from_sequence(self, sequence: Sequence):
        """ Creates a pulseq-style sequence definition from a cmrseq.sequence object.

        """

        self.version = "1.4.0"
        self.raster_times = dict(rf=sequence._system_specs.rf_raster_time,
                                 grad=sequence._system_specs.grad_raster_time,
                                 adc=sequence._system_specs.adc_raster_time)
        self.raster_times["blocks"] = max(self.raster_times.values())

        self.additional_defs = {k: sequence._system_specs.__getattribute__(k) for k in
                                ("rf_dead_time", "rf_ringdown_time", "rf_lead_time",
                                 "adc_dead_time", "rf_peak_power", "max_grad", "max_slew")}

        rf_dead_time = np.round(self.additional_defs["rf_dead_time"].m_as("ms"), decimals=8)
        adc_dead_time = np.round(self.additional_defs["adc_dead_time"].m_as("ms"), decimals=8)

        self.block_array = []

        # Create a set of double ended cues to 'stream'-interleave the event definitions, based
        # on the start-time of the blocks
        t, (gx, gy, gz) = sequence.combined_gradients()

        gx_que = deque(cmrseq.utils.find_gradient_blocks(t, gx)
                       + [("dummy", (sys.float_info.max,))])
        gy_que = deque(cmrseq.utils.find_gradient_blocks(t, gy)
                       + [("dummy", (sys.float_info.max,))])
        gz_que = deque(cmrseq.utils.find_gradient_blocks(t, gz)
                       + [("dummy", (sys.float_info.max,))])
        rf_que = deque(sequence.get_block(typedef=cmrseq.bausteine.RFPulse)
                       + [SimpleNamespace(tmin=Quantity(sys.float_info.max, "ms"))])
        adc_que = deque(sequence.get_block(typedef=cmrseq.bausteine.ADC)
                        + [SimpleNamespace(tmin=Quantity(sys.float_info.max, "ms"))])
        all_queues: dict[str: deque] = dict(RF=rf_que, GX=gx_que, GY=gy_que, GZ=gz_que, ADC=adc_que)
        key_list = list(all_queues.keys())

        # Combine queues as (blocktype, tmin, tmax, block_def)
        combined_que: deque[(str, float, float, Any)] = deque()
        while any([len(_) > 1 for _ in all_queues.values()]):
            # Dead time is accounted for during block sorting
            min_idx = min(range(5), key=lambda x: [rf_que[0].tmin.m_as("ms") - rf_dead_time,
                                                   gx_que[0][1][0],
                                                   gy_que[0][1][0],
                                                   gz_que[0][1][0],
                                                   adc_que[0].tmin.m_as("ms") - adc_dead_time][x])
            blocktype = key_list[min_idx]
            block_def = all_queues[blocktype].popleft()

            if blocktype in ["RF", "ADC"]:
                block_min = np.round(block_def.tmin.m_as("ms"), decimals=8)
                block_max = np.round(block_def.tmax.m_as("ms"), decimals=8)
                # Dead times can be added here, to ensure that the dead times are obeyed by the splitting algorithm
                if blocktype == "RF":
                    # For now we will use the rf dead time for both the start and end delay.
                    block_max += rf_dead_time
                    block_min -= rf_dead_time
                else:
                    # Same for ADC with adc dead time
                    block_max += adc_dead_time
                    block_min -= adc_dead_time

            else:
                block_min = block_def[1][0]
                block_max = block_def[1][-1]

            # A negative block min might happen if a sequence is badly constructed (starts with an RF pulse)
            # If this is the case we throw an error 
            if block_min < 0:
                raise ValueError(f"Encountered negative block start time trigger by {blocktype}. Ensure the sequence does not start with an RF or ADC without an appropriate delay.")
            combined_que.append((blocktype, block_min, block_max, block_def))
        combined_que.append(("GX",sys.float_info.max,sys.float_info.max, ("dummy", (sys.float_info.max,))))
        total_number_of_blocks = len(combined_que) - 1

        # In a loop add event definitions into the current block entry, and finalize the block
        # if block borders are detected (consecutive events on the same channel)
        current_block_entry = {"RF": None, "GX": None, "GY": None, "GZ": None,
                               "ADC": None, "EXT": None}
        progress_bar = tqdm(range(total_number_of_blocks),
                            desc="Converting to Pulseq blocks")

        tmp_type_que = deque()
        tmp_def_que = deque()
        while len(combined_que) > 1:
            progress_bar.n = total_number_of_blocks - len(combined_que)
            progress_bar.refresh()
            ## Pull blocks until a collision by type is found
            while combined_que[0][0] not in tmp_type_que and len(combined_que) > 1:
                curr_type, new_block_min, new_block_max, block_def = combined_que.popleft()
                tmp_type_que.append(curr_type)
                tmp_def_que.append((new_block_min, new_block_max, block_def))

            if len(combined_que) == 1:
                current_block_entry.update({btype: bdef for btype, (_, _, bdef)
                                            in zip(tmp_type_que, tmp_def_que)})
                block_start = tmp_def_que[0][0]
                block_end = np.max([b[1] for b in tmp_def_que])
                # Add some extra raster to block_end to account for possible ADC dead time
                # This is ok, since it is the end of the sequence?????
                block_end = block_end + self.raster_times["blocks"].m_as('ms')
                self._register_block(current_block_entry, block_start, block_end - block_start,
                                     sequence._system_specs)
                current_block_entry = {"RF": None, "GX": None, "GY": None, "GZ": None,
                                       "ADC": None, "EXT": None}
                break

            # Sometimes the set of blocks can be split into two groups, if there is no overlap
            # While this increases the number of blocks, it produces a more intuitive splitting
            blocks_starts = np.around(np.array([b[0] for b in tmp_def_que]), decimals=8)
            blocks_ends = np.around(np.array([b[1] for b in tmp_def_que]), decimals=8)
            max_block_end = blocks_ends[0]
            for idx in range(1,len(blocks_starts)):
                if blocks_starts[idx]<max_block_end:
                    # this block is in the keep group
                    if max_block_end<blocks_ends[idx]:
                        max_block_end = blocks_ends[idx]
            
            while tmp_def_que[-1][0] >= max_block_end:
                combined_que.appendleft((tmp_type_que.pop(), *tmp_def_que.pop()))
            
            coliding_block_min = combined_que[0][1]
            # Easiest case: # All block are ending before the next one starts:
            if all([b[1] <= coliding_block_min for b in tmp_def_que]):
                current_block_entry.update({btype: bdef for btype, (_, _, bdef)
                                            in zip(tmp_type_que, tmp_def_que)})
                block_start = tmp_def_que[0][0]
                block_end = coliding_block_min
                self._register_block(current_block_entry, block_start, block_end - block_start,
                                     sequence._system_specs)
                current_block_entry = {"RF": None, "GX": None, "GY": None, "GZ": None,
                                       "ADC": None, "EXT": None}
                tmp_def_que.clear(), tmp_type_que.clear()
                continue


            # Collision can't be solved by poping blocks from queue, hence splitting the gradients
            # in the current block definition at the colliding definition start time.
            # Assumptions for this block collision:
            # 1. RF and ADCs have absolute priority for definining block borders, they are
            # always fully contained in a block.
            # 2. Gradients are allowed to be split. Hence, when a block collision occurs,
            # All gradient channels of the previous block are split such that the second part is
            # included into the next block as arbitrary waveform.
            else:
                current_block_entry.update(
                    {btype: bdef for btype, (_, _, bdef) in zip(tmp_type_que, tmp_def_que)})
                block_start = tmp_def_que[0][0]
                block_end = coliding_block_min
                splitting_time = np.around(np.floor(
                    np.around(block_end / self.raster_times["blocks"].m_as("ms"), decimals=6)
                ) * self.raster_times["blocks"].m_as("ms"), decimals=6)

                # There is an edge case, where multiple gradient blocks occur on the same channel during the RF pulse or ADC
                # In this case, these blocks need to be merged and split at the end of the RF pulse
                if current_block_entry["RF"] is not None:
                    # Update splitting time if RF pulse finishes after the collision
                    splitting_time = np.maximum(current_block_entry["RF"].tmax.m_as("ms")+rf_dead_time,splitting_time)
                if current_block_entry["ADC"] is not None:
                    # Update splitting time if ADC finishes after the collision
                    splitting_time = np.maximum(current_block_entry["ADC"].tmax.m_as("ms")+adc_dead_time,splitting_time)
                # Splitting time must sit on block rater
                # There are edge cases when ADCs are on a raster lower than block raster and they are too close
                # But in this case, no sequence can be written.
                splitting_time = np.around(np.ceil(np.around(splitting_time / self.raster_times["blocks"].m_as("ms"), decimals=6)) * 
                                           self.raster_times["blocks"].m_as("ms"), decimals=6)
                
                # Go through que, popping objects that start before the splitting time
                while (combined_que[0][1] < splitting_time) and len(combined_que) > 1:
                    
                    btype = combined_que[0][0]
                    if btype == "RF":
                        if current_block_entry["RF"] is not None:
                            # RF pulse already in block, meaning there is a problem
                            # Either due to overlap of RF pulses, or an ADC object overlapping 2 RF pulses
                            raise ValueError("RF pulse overlap")
                        else:
                            # The next block is a RF pulse, and overlaps with the current splitting time
                            # We add it to the current block entry, and update the splitting time
                            curr_type, new_block_min, new_block_max, block_def = combined_que.popleft()
                            tmp_type_que.append(curr_type)
                            tmp_def_que.append((new_block_min, new_block_max, block_def))
                            current_block_entry.update({btype: bdef for btype, (_, _, bdef) in zip(tmp_type_que, tmp_def_que)})
                            splitting_time = np.maximum(current_block_entry["RF"].tmax.m_as("ms"),splitting_time)

                    # Similar to above, but for ADC
                    elif btype == "ADC":
                        if current_block_entry["ADC"] is not None:
                            # ADC already in block, meaning there is a problem
                            # Either due to overlap of ADCs, or a RF object overlapping 2 ADCs
                            raise ValueError("ADC overlap")
                        else:
                            # The next block is an ADC, and overlaps with the current splitting time
                            # We add it to the current block entry, and update the splitting time
                            curr_type, new_block_min, new_block_max, block_def = combined_que.popleft()
                            tmp_type_que.append(curr_type)
                            tmp_def_que.append((new_block_min, new_block_max, block_def))
                            current_block_entry.update({btype: bdef for btype, (_, _, bdef) in zip(tmp_type_que, tmp_def_que)})
                            splitting_time = np.maximum(current_block_entry["ADC"].tmax.m_as("ms"),splitting_time)
                    
                    else: # The next block is a gradient
                        if current_block_entry[btype] is None:
                            # Gradient not in block, meaning there is no problem
                            # We add it to the current block entry, and update the splitting time
                            curr_type, new_block_min, new_block_max, block_def = combined_que.popleft()
                            tmp_type_que.append(curr_type)
                            tmp_def_que.append((new_block_min, new_block_max, block_def))
                            current_block_entry.update({btype: bdef for btype, (_, _, bdef) in zip(tmp_type_que, tmp_def_que)})
                            # In some cases, this gradient block starts only a few samples before the splitting time
                            # This can result in < 2 samples of gradient, which may not be handled well by pulseq
                            # Hence, we check this case and if needed increase the splitting time
                            if splitting_time - new_block_min < self.raster_times["grad"].m_as("ms") * 2:
                                ext_time = int(np.ceil((splitting_time - new_block_min)/ self.raster_times["grad"].m_as("ms")))
                                ext_time = ext_time * self.raster_times["grad"].m_as("ms")
                                splitting_time = new_block_min + ext_time
                        else:
                            # Gradient already in block, so they need to be merged
                            _, _, _, block_def = combined_que.popleft()
                            block_merged = self._merge_gradient_events(current_block_entry[btype], block_def)
                            # Get index in que
                            idx = tmp_type_que.index(btype)
                            # Update the block definition
                            tmp_def_que[idx] = (block_merged[1][0],block_merged[1][-1], block_merged)
                            current_block_entry.update({btype: bdef for btype, (_, _, bdef) in zip(tmp_type_que, tmp_def_que)})
                            # We do not update splitting time, since we can split gradients

                for btype, (bmin, bmax, bdef) in zip(tmp_type_que, tmp_def_que):
                    if btype in ("GX", "GY", "GZ") and bmax > splitting_time:
                        # If point is already contained in the definition, use it as index
                        if np.any(is_close := np.isclose(bdef[1], splitting_time,rtol=0)):
                            insertion_index = np.squeeze(np.argwhere(is_close))
                            insertion_val = bdef[2][insertion_index]
                            tmp_wf = bdef[2]
                            tmp_t = bdef[1]
                        # Else interpolate the waveform, insert the point and split at this location
                        else:
                            insertion_index = np.searchsorted(bdef[1], splitting_time)
                            insertion_val = np.interp(splitting_time, bdef[1], bdef[2])
                            tmp_wf = np.insert(bdef[2], insertion_index, insertion_val)
                            tmp_t = np.insert(bdef[1], insertion_index, splitting_time)
                        current_block_entry[btype] = ("arbitrary", tmp_t[:insertion_index + 1],
                                                      tmp_wf[:insertion_index + 1])
                        combined_que.appendleft((btype, tmp_t[insertion_index], tmp_t[-1],
                                                 ("arbitrary", tmp_t[insertion_index:],
                                                  tmp_wf[insertion_index:])))
                        
                self._register_block(current_block_entry, block_start, splitting_time - block_start,
                                     sequence._system_specs)
                current_block_entry = {"RF": None, "GX": None, "GY": None, "GZ": None,
                                       "ADC": None, "EXT": None}
                tmp_def_que.clear(), tmp_type_que.clear()

        self.block_array = np.stack(self.block_array)

    def _register_block(self, curr_block: dict, previous_break_point: float,
                        duration: float, system_specs: 'cmrseq.SystemSpec'):
        """Converts the dictionary of block definitions into Pulseq-table rows.

        :param curr_block: dict[str: block_def]
        :param previous_break_point: in millisecond
        :param duration: in millisecond
        :param system_specs: Systemspecifications object
        """
        rf_id, adc_id, ext_id = 0, 0, 0
        if (block := curr_block["RF"]) is not None:
            rf_id = self._register_rf_event(block, previous_break_point,
                                            system_specs.rf_raster_time.m_as("ms"),
                                            system_specs.gamma)

        if (block := curr_block["ADC"]) is not None:
            adc_id = self._register_adc_event(block, previous_break_point)

        gradient_ids = [0, 0, 0]
        grad_blocks = [(i, curr_block[j]) for i, j in zip(range(3), ("GX", "GY", "GZ"))
                       if curr_block[j] is not None]
        for idx, block in sorted(grad_blocks, key=lambda x: x[1][1][0]):
            gradient_ids[idx] = self._register_gradient_event(
                                                        block, previous_break_point,
                                                        system_specs.grad_raster_time.m_as("ms"),
                                                        system_specs.gamma)

        block_raster = max([system_specs.grad_raster_time.m_as("ms"),
                            system_specs.rf_raster_time.m_as("ms"),
                            system_specs.adc_raster_time.m_as("ms")])
        duration = np.round(duration / block_raster, decimals=8).astype(int)
        self.block_array.append((len(self.block_array) + 1, duration,
                                 rf_id, *gradient_ids, adc_id, ext_id))

    def _register_rf_event(self, block: cmrseq.bausteine.RFPulse,
                           previous_break_point: float, raster_time: float,
                           gamma: Quantity) -> int:
        """Inserts RF event definition into the Pulseq RF table, using the shape table to store
        the waveform and phase as well as time-points if not defined on raster.

        :param block: cmrseq.RFPulse instance
        :param previous_break_point: in milliseconds
        :param raster_time: in milliseconds
        :param gamma:
        :return: Event index
        """
        normed_wf, peak_amp, phase, time = block.normalized_waveform
        phase_offset = block.phase_offset
        # Pulseq requires positive RF amplitudes, so we adjust phase offset if negative
        if peak_amp.m_as("uT") < 0:
            peak_amp = -peak_amp
            phase_offset += Quantity(np.pi,"rad")

        # Check if RF definition is on raster
        unique_dt = np.unique(np.around(np.diff(time.m_as("ms")), decimals=8))
        if len(unique_dt) == 1 and np.isclose(unique_dt[0], raster_time, atol=1e-6):
            time_id = 0
            normed_wf = self.shift_definition(normed_wf)
            # AS the first and last RF points in cmrseq must be zero in amplitude, the phase is
            # also always evaluated as 0 in block.normalized_waveform. The half-rastertime shift
            # results in wrong halfed phase value in after interpolation, hence the first and last
            # elements are set to the second and second to last values
            phase[[0, -1]] = phase[[1, -2]]
            phase = self.shift_definition(phase)
        else:
            time_shape = np.around((time.m_as("ms") - time[0].m_as("ms")) / raster_time).astype(int)
            time_id = self.check_add_shape(time_shape)
        wf_id = self.check_add_shape(normed_wf)
        phase_id = self.check_add_shape(np.around(phase / np.pi / 2, decimals=6))
        delay = np.round(block.tmin.m_as("ms") - previous_break_point, decimals=6) * 1000
        rf_def = (peak_amp.m_as("uT") / gamma.m_as("Hz/uT"),
                  wf_id, phase_id, time_id, delay,
                  block.frequency_offset.m_as("Hz"), phase_offset.m_as("rad"))
        rf_id = self.check_add_def(rf_def, self.rf_hash_table)
        self.rf_table[rf_id] = dict(phase_offset=phase_offset,
                                    frequency_offset=block.frequency_offset,
                                    delay=Quantity(delay, "us"),
                                    shape_ids=[wf_id, phase_id, time_id],
                                    amplitude=peak_amp * gamma.to("Hz/uT"))
        return rf_id

    def _register_adc_event(self, block: cmrseq.bausteine.ADC, previous_break_point: float) -> int:
        """Inserts ADC event into the Pulseq table.

        :param block: ADC object
        :param previous_break_point: in milliseconds
        :return: Event index
        """
        timings = block.adc_timing
        dwell = np.around((timings[1] - timings[0]).m_as("ns"), decimals=0).astype(int)
        if not np.isclose(dwell, (timings[1] - timings[0]).m_as("ns"), atol=1e-2):
            raise ValueError(f"Encountered invalid adc dwell not on integer ns {block}")

        num_samples = timings.shape[0]
        # ADC delay should be rounded down to the nearest us
        # This is shortcoming of the pulseq format?
        delay = np.round((block.tmin.m_as("ms") - previous_break_point) * 1000,
                         decimals=6).astype(int)
        
        # if not np.isclose(delay / 1000 - block.tmin.m_as("ms") + previous_break_point, 0.,
        #                   atol=1e-8):
        #     raise ValueError(f"Encountered invalid adc delay not on integer us"
        #                      f" {block.tmin.m_as('ms') - previous_break_point} vs {delay / 1000}")

        adc_def = (num_samples, dwell, delay, block.phase_offset.m_as("rad"),
                   block.frequency_offset.m_as("Hz"))
        adc_id = self.check_add_def(adc_def, self.adc_hash_table)
        self.adc_table[adc_id] = dict(num_samples=num_samples, dwell=Quantity(dwell, "ns"),
                                      delay=Quantity(delay, "us"),
                                      frequency_offset=block.frequency_offset,
                                      phase_offset=block.phase_offset)
        return adc_id

    def _register_gradient_event(self, block: tuple[str, tuple[np.ndarray, np.ndarray]],
                                 previous_break_point: float, raster_time: float,
                                 gamma: Quantity) -> int:
        """Inserts gradient event into trapezoid and arbitrary tables with contiguous indexing

        :param block: gradient definition as (type ["trapezoid"/"arbitrary"], time-point, waveform)
        :param previous_break_point: as milliseconds
        :param raster_time: as milliseconds
        :return: Event index
        """
        last_id = len(self.traps_table) + len(self.grads_table)
        if block[0] == "trapezoid":
            amplitude = block[2][1]
            rise = np.round(block[1][1] - block[1][0], decimals=6)
            fall = np.round(block[1][-1] - block[1][-2], decimals=6)
            flat = np.round(block[1][-1] - block[1][0] - rise - fall, decimals=6)
            delay = np.round(block[1][0] - previous_break_point, decimals=6)
            def_tuple = (amplitude, rise, flat, fall, delay)
            gradient_id = self.check_add_def(def_tuple, self.traps_hash_table, last_id)
            self.traps_table[gradient_id] = dict(
                amplitude=Quantity(amplitude, "mT/m") * gamma.to("Hz/mT"),
                rise_time=Quantity(rise, "ms"),
                flat_duration=Quantity(flat, "ms"),
                fall_time=Quantity(fall, "ms"),
                delay=Quantity(delay, "ms"))
        else:
            amp_minmax = [np.min(block[2]), np.max(block[2])]
            amplitude = amp_minmax[np.argmax(np.abs(amp_minmax))]
            # This should never really happen, but just in case
            if np.abs(amplitude)>0:
                normed_wf = block[2] / amplitude
            else:
                normed_wf = block[2]*0

            # Check if Grad definition is on raster
            unique_dt = np.unique(np.around(np.diff(block[1]), decimals=8))
            if len(unique_dt) == 1 and np.isclose(unique_dt[0], raster_time, atol=1e-6):
                normed_wf = self.shift_definition(normed_wf)
                time_id = 0
            else:
                # In pulseq the time-shapes always start with zero, hence the first time needs
                # to be subtracted. The temporal shift with regard to the block border is contained
                # in the 'delay' field
                time_shape = np.round(
                    ((np.array(block[1]) - block[1][0]) / raster_time) + 1e-8).astype(int)
                time_id = self.check_add_shape(time_shape)

            gwf_id = self.check_add_shape(np.around(normed_wf + 1e-9, decimals=8))
            def_tuple = (amplitude, gwf_id, time_id, block[1][0] - previous_break_point)
            gradient_id = self.check_add_def(def_tuple, self.grads_hash_table, last_id)
            self.grads_table[gradient_id] = dict(
                amplitude=Quantity(amplitude, "mT/m") * gamma.to("Hz/mT"),
                shape_ids=[gwf_id, time_id],
                delay=Quantity(block[1][0] - previous_break_point, "ms"))
        return gradient_id
    
    def _merge_gradient_events(self, block1: tuple[str, np.ndarray, np.ndarray],
                               block2: tuple[str, np.ndarray, np.ndarray]):
        
        # Merge gradients to produce a new arbitrary gradient

        if (block1[0] != "arbitrary" and block1[0] != "trapezoid") or (block2[0] != "arbitrary" and block2[0] != "trapezoid"):
            raise ValueError("Only gradients can be merged")

        # block1 should occur first
        if block1[1][0] > block2[1][0]:
            temp = block1
            block2 = block1
            block1 = temp
        
        if block1[1][-1] > block2[1][0]:
            # Block overlap is not allowed
            raise ValueError("Can not merge overlapping blocks")
        
        
        if np.isclose(block1[1][-1],block2[1][0],rtol=0, atol=1e-6):
            # Blocks share first/last time
            # this is only valid if gradient strengths are the same
            if not np.isclose(block1[2][-1],block2[2][0],rtol=0, atol=1e-6):
                raise ValueError("Can not merge overlapping blocks (different gradient strengths)")
            # merge blocks
            t_new = np.concatenate([block1[1],block2[1][1:]])
            g_new = np.concatenate([block1[2],block2[2][1:]])
        else:
            t_new = np.concatenate([block1[1],block2[1]])
            g_new = np.concatenate([block1[2],block2[2]])

        return ("arbitrary", t_new, g_new)


    @staticmethod
    def shift_definition(waveform: np.ndarray):
        x_old = np.arange(0, waveform.shape[0], dtype=np.float64)
        x_new = x_old[:-1] + 0.5
        return np.interp(x_new, x_old, waveform)

    def check_add_shape(self, arr: np.ndarray) -> int:
        """Checks if specified array is already in self.shape_table (if not adds it to the table)
        and returns the corresponding shape_id.

        Lookup is performed by computing the hash value of the array which serves as key of the
        shape_table dictionary.

        :param arr:
        :return: shape_id int
        """
        hash_value = hash(arr.tobytes())
        existing_entry = self.shape_hash_table.get(hash_value, None)
        if existing_entry is None:
            shape_id = len(self.shape_table) + 1  # this should be O(1)
            self.shape_hash_table[hash_value] = shape_id
            self.shape_table[shape_id] = arr.flatten()
        else:
            shape_id = existing_entry
        return shape_id

    @staticmethod
    def check_add_def(def_tuple: tuple, table: dict[int: tuple], last_id: int = None) -> int:
        """Checks if definition tuple is already in self.rf_table (if not adds it to the table)
        and returns the corresponding rf_id.

        Lookup is performed by computing the hash value of the stringified definition tuple
        which serves as key of the rf_table dictionary.


        :param def_tuple: RF definition as specified in the Pulseq package (amp, magnitude_id,
            phase_id, time_id, delay, frequency_offset, phase_offset)
        :param table: One of the following lookup dictionaries
            [file.rf_table, file.adc_table, file.trap_table, file.arb_table]
        :param last_id: if specified, the new entry is inserted at last_id + 1 otherwise the last
            id is computed as the length of table.
        :return: definition id is corresponding table
        """
        # deal with rounding issues and negative zeroes
        def_tuple = [np.round(x + 0.0, decimals=6) for x in def_tuple]
        hash_value = hash(str(def_tuple))
        
        existing_entry = table.get(hash_value, None)
        if existing_entry is None:
            if last_id is None:
                def_id = len(table) + 1  # this should be O(1)
            else:
                def_id = last_id + 1
            table[hash_value] = (def_id, *def_tuple)
        else:
            def_id = existing_entry[0]
        return def_id