""" Module containing the implementation of sampling blocks"""
__all__ = ["ADC", "SymmetricADC", "GridSamplingADC"]

import decimal
import warnings

import math

import numpy as np
from pint import Quantity

from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core._system import SystemSpec
from cmrseq._exceptions import BuildingBlockValidationError, AutomaticOptimizationWarning
from cmrseq._exceptions import BuildingBlockArgumentError


class ADC(SequenceBaseBlock):
    """ ADC-specific extension to the SequenceBaseBlock, serves as base class for all
    ADC implementations.

    :param system_specs: System Limits specification object
    :param name:
    :param adc_timing: Quantity array of dimension time, containing all sampling event timings.
    :param adc_center: Time point defining the center of the ADC object
    :param phase_offset:  Phase-offset for all adc-samples, added when computing the adc-phase.
    :param frequency_offset: Frequency offset for all adc-samples, converted to an additional phase
                            offset per sample
    """
    #: Timing of ADC-sampling events. Exact definition of the meaning of that sampling time
    #: is delegated to subclass implementation. Quantity[ms]
    adc_timing: Quantity
    #: Time defining the center of the adc-events. Meant to synchronize the ADC block with echo
    #: times. Quantity[ms]
    adc_center: Quantity
    #: Phase-offset for all adc-samples, added when computing the adc-phase property. Quantity[rad]
    phase_offset: Quantity
    #: Frequency offset for all adc-samples, converted to an additional phase offset per sample and
    #: added when computing the adc-phase property. Quantity[Hz]
    frequency_offset: Quantity

    def __init__(self, system_specs: SystemSpec, name: str,
                 adc_timing: Quantity, adc_center: Quantity,
                 frequency_offset: Quantity, phase_offset: Quantity):
        self.adc_timing: Quantity = adc_timing.to("ms")
        self.adc_center: Quantity = adc_center.to("ms")
        self.frequency_offset: Quantity = frequency_offset.to("Hz")
        self.phase_offset: Quantity = phase_offset.to("rad")
        super().__init__(system_specs, name)

    @property
    def adc_phase(self) -> Quantity:
        """Returns the phase :math:`\\phi_s` at each adc sample :math:`s` in radians given the
        phase offset :math:`\\phi_0` and frequency offset :math:`\\delta f` according to the
        formular:

        .. math::

            \\phi_s = \\phi_0 + 2 * \\pi * \\delta f
        """
        t = self.adc_timing
        t_zero_ref = t - t[0]
        phase_per_time = (self.phase_offset.m_as("rad") +
                          2 * np.pi * self.frequency_offset.m_as("kHz") * t_zero_ref.m_as("ms"))
        return phase_per_time

    @property
    def tmin(self) -> Quantity:
        """ Returns the time of the first sampling event."""
        return self.adc_timing[0]

    @property
    def tmax(self) -> Quantity:
        """ Returns the time of the last sampling event."""
        return self.adc_timing[-1]

    def validate(self, system_specs: SystemSpec):
        """Validates the dwell time against the system_specs, ensuring it sits on the ADC raster time."""
        unique_dwell_times = np.unique(np.round(np.diff(self.adc_timing.m_as("ms")), decimals=6))
        n_dwell =  np.round(unique_dwell_times/np.round(system_specs.adc_raster_time.m_as("ms"), decimals=6), decimals=6)
        dwell_remainder = np.mod(n_dwell, 1)
        if not np.allclose(dwell_remainder, 0., atol=1e-4):
            raise BuildingBlockValidationError(f"ADC dwell-time is not multiple of ADC-raster time"
                                               f"\n\t  {unique_dwell_times} \n\t {dwell_remainder}")

    def shift(self, time_shift: Quantity) -> None:
        """Adds the time-shift to all adc definition points and the adc-center"""
        time_shift = time_shift.to("ms")
        self.adc_timing += time_shift
        self.adc_center += time_shift

    def flip(self, time_flip: Quantity = None):
        """Flips the adc-timing and adc-center around the given time point."""
        if time_flip is None:
            time_flip = self.tmax
        self.adc_timing = np.flip(time_flip.to("ms") - self.adc_timing, axis=0)
        self.adc_center = np.flip(time_flip.to("ms") - self.adc_center, axis=0)

    def snap_to_raster(self, system_specs: SystemSpec) -> None:
        pass


class SymmetricADC(ADC):
    """ ADC with instantaneous encoding events at k-space positions.

    Defines an ADC with sampling events uniformly distributed over
    the given duration. The central time point is allways contained as sampling event.
    
    Sample time always corresponds to the center of the sampling event

    :param num_samples: number of sampling events over duration
    :param system_specs: cmrseq.SystemSpec object
    :param dwell: Quantity[time] Interval length associated with 1 sampling event.
                        Corresponds to kspace extend in readout-direction :math:`(1/FOV_{kx})`.
    :param duration: Quantity[time] Total sampling duration corresponding to
                        :math:`(1 / \\Delta k_x)`.
                      Usually is the same as flat_duration of accompanying trapezoidal gradient.
    :param delay: Quantity[time] Leading time without sampling events
    :param frequency_offset: Adds a linearly increasing phase over the ADC duration, used for e.g.
                    RF-spoiling or in-plane FOV shift.
    :param phase_offset: Adds a constant phase offset to the adc, e.g. in RF spoiling
    """
    #: Total number of samples.
    _n_samples: int
    #:
    _dwell: Quantity

    def __init__(self, system_specs: SystemSpec,
                 num_samples: int,
                 dwell: Quantity = None,
                 duration: Quantity = None,
                 delay: Quantity = None,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "adc"):

        if (dwell is None and duration is None) or not (dwell is None or duration is None):
            raise ValueError("Either dwell or duration must be defined")

        if duration:
            dwell = duration / num_samples
        delay = Quantity(0, "ms") if delay is None else delay
        adc_timing = (np.arange(0, num_samples) + 0.5) * dwell + delay

        frequency_offset = frequency_offset.to("Hz")
        phase_offset = phase_offset.to("rad")

        self._n_samples = int(num_samples)
        self._dwell = dwell
        adc_center = adc_timing[int(np.floor(num_samples / 2))]

        super().__init__(system_specs=system_specs, name=name,
                         adc_timing=adc_timing, adc_center=adc_center,
                         phase_offset=phase_offset,
                         frequency_offset=frequency_offset)

    @property
    def tmin(self) -> Quantity:
        """ Returns the time of the first sampling event. Behavior varies for odd/even number of
        samples:

        Returns the time of the first sampling event minus half a dwell time on gradient raster time.

        In both cases this corresponds to the start of the plateau of a readout gradient
        """
        
        return self.adc_timing[0] - self._dwell / 2

    @property
    def tmax(self) -> Quantity:
        """Returns the time of the last sampling event. Behavior varies for odd/even number of
        samples:

        Returns the time of the last sampling event plus half a dwell time.

        In both cases this corresponds to the end of the plateau of a readout gradient
        """
        
        return self.adc_timing[-1] + self._dwell / 2

    @classmethod
    def from_centered_valid(cls, system_specs: SystemSpec, num_samples: int, duration: Quantity,
                            delay: Quantity = Quantity(0.,'ms'), frequency_offset: Quantity = Quantity(0., "Hz"),
                            phase_offset: Quantity = Quantity(0., "rad"), name="adc", suppress_warnings=False
                            ) -> 'SymmetricADC':
        """Creates an ADC block with valid duration (dwell time on raster) where the stated duration
         is the upper bound (altered by at max num_samples * adc_raster_time). The difference in
        duration is padded around at the start and end of the block to maintain the center.

        Guarantees to have a sample at the exact half duration of the ADC block.

        :param num_samples: number of sampling events over duration
        :param system_specs: cmrseq.SystemSpec object
        :param duration: target duration that is modified such that the resulting dwell time is on
                    the adc raster
        :param delay: Quantity[time] Leading time without sampling events
        :param frequency_offset: Adds a linearly increasing phase over the ADC duration, used for e.g.
                        RF-spoiling or in-plane FOV shift.
        :param phase_offset: Adds a constant phase offset to the adc, e.g. in RF spoiling
        """
        dwell = duration / num_samples
        if not system_specs.is_on_raster(dwell, "adc")[0]:
            valid_dwell = (system_specs.time_to_raster(duration / num_samples, "adc")
                           - system_specs.adc_raster_time)
            if valid_dwell<system_specs.adc_raster_time:
                raise ValueError("ADC dwell time is smaller than raster. Either increase ADC duration or decrease number of samples.")
            
            valid_duration = np.round((num_samples * valid_dwell).to("ms"), decimals=6)
            duration_diff = np.round((duration - valid_duration).to("ms"), decimals=6)

            if not system_specs.is_on_raster(duration_diff / 2, "adc")[0]:
                valid_dwell -= system_specs.adc_raster_time
                valid_duration = np.round((num_samples * valid_dwell).to("ms"), decimals=6)
                duration_diff = np.round((duration - valid_duration).to("ms"), decimals=6)
            delay = delay + system_specs.time_to_raster(duration_diff.to("ns") / 2, "adc")
            if not suppress_warnings:
                warnings.warn(f"In SymmetricADC.from_centered_valid() modified duration to get"
                            f" a valid dwell time:\n\t\t{duration=}\n\t\t{valid_duration=}.\n\t"
                            f"+ To avoid this, make sure duration/num_samples is a multiple"
                            f" of system_specs.adc_raster_time", AutomaticOptimizationWarning)
        else:
            valid_duration = duration
        return cls(system_specs, num_samples, duration=valid_duration, delay=delay,
                   frequency_offset=frequency_offset, phase_offset=phase_offset, name=name)


class GridSamplingADC(ADC):
    """ Defines an oversampling adc-block on system adc_raster_time.

    :param system_specs: SystemSpec instance
    :param duration: Duration over which the ADC is active on raster time. Is assumed to be on
            adc-raster-time
    :param delay: Leading time before the ADC block starts. Is assumed to be on adc-raster-time
    :param frequency_offset: Linear phase evolution that is added to the demodulation
                        over the ADC duration
    :param phase_offset: Phase offset that is added to the demodulation
    :param name: defaults to 'adc'
    """
    def __init__(self, system_specs: SystemSpec,
                 duration: Quantity,
                 delay: Quantity = Quantity(0, "ms"),
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "adc"):
        rounded_raster_time = decimal.Decimal(
            str(float(np.round(system_specs.adc_raster_time.m_as("ms"), decimals=6))))
        delay_dec = decimal.Decimal(str(float(np.round(delay.m_as("ms"), decimals=6))))
        duration_dec = decimal.Decimal(str(float(np.round(duration.m_as("ms"), decimals=6))))
        if delay_dec % rounded_raster_time != decimal.Decimal("0.0"):
            raise BuildingBlockArgumentError(f"Specified delay {delay:1.6} is not"
                                             f" on adc_raster_time", argument="delay",
                                             class_name="GridSamplingADC")
        if duration_dec % rounded_raster_time != decimal.Decimal("0.0"):
            raise BuildingBlockArgumentError(f"Specified duration {duration:1.6} is not"
                                             f" on adc_raster_time", argument="duration",
                                             class_name="GridSamplingADC")
        n_steps = math.ceil(duration / system_specs.adc_raster_time)
        time_grid = np.arange(0, n_steps + 1, 1) * system_specs.adc_raster_time.m_as("ms")

        super().__init__(system_specs=system_specs, name=name,
                         adc_timing=Quantity(time_grid, "ms") + delay,
                         adc_center=system_specs.time_to_raster(duration / 2, "adc") + delay,
                         frequency_offset=frequency_offset,
                         phase_offset=phase_offset)

    @property
    def tmin(self) -> Quantity:
        """ Returns the time of the first sampling event."""
        return self.adc_timing[0]

    @property
    def tmax(self) -> Quantity:
        """ Returns the time of the last sampling event."""
        return self.adc_timing[-1]
