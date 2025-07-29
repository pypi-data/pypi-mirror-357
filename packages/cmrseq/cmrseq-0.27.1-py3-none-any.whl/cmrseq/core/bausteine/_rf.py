""" This module contains in the implementation of radio-frequency pulse building blocks"""
__all__ = ["RFPulse", "SincRFPulse","HardRFPulse", "GaussRFPulse", "ArbitraryRFPulse",
           "AdiabaticRFPulse", "SLRPulse"]

from typing import Tuple
from warnings import warn
import math
import cmath

from pint import Quantity
import numpy as np

import cmrseq
from cmrseq.core.bausteine._base import SequenceBaseBlock
from cmrseq.core._system import SystemSpec


class RFPulse(SequenceBaseBlock):
    """Generic MRI-sequence radio-frequency building block

    This class implements all functionality that should be provided by all subtypes of
    RF-pulses.

    The waveform (assuming linear interpolation between the points) and the time-points have to
    be specified on construction of the RF object, where the waveform is assumed to be real-valued.
    It also is assumed, that all RF-pulse subclasses correctly calculate and provide the following
    quantities:

    1. Pulse bandwidth
    2. Frequency offset
    3. Phase offset

    The phase offset and frequency offset attributes are used to compute the complex rf-waveform
    representation using the `RFPulse.rf` - property.

    :param system_specs: SytemSpecifications object
    :param name: string
    :param time: (# points) time-points defining the waveform duration
    :param rf_waveform: (#points) rf-amplitude
    :param phase_offset: Offset in radians, that is added when computing the complex-valued
                         RF-waveform in RFPulse.rf
    :param frequency_offset: Linear phase contribution, that is added when computing the
                            complex-valued RF-waveform in RFPulse.rf
    :param rf_events: Tuple containing pairs of events defined as (center-time, flip-angle)
    :param snap_to_raster: if True, all points in the rf definition are rounded to the nearest
                            raster point.
    """
    #: Tuple containing defining points of RF-waveforms as np.array (wrapped as Quantity)
    #: with shape (time: (t, ), waveform: (t, )). Between points, linear interpolation is assumed
    _rf: Tuple[Quantity, Quantity]
    #: Tuple containing rf events (time, flip_angle)
    rf_events: Tuple[Quantity, Quantity]
    #: RF pulse bandwidth in kilo Hertz. Used to calculate gradient strength
    bandwidth: Quantity
    #: RF phase offset in radians. This is used phase shift the complex rf amplitude in self.rf
    phase_offset: Quantity
    #: RF frequency offset in Hertz. This is used to modulate the complex rf amplitude in self.rf
    frequency_offset: Quantity

    def __init__(self, system_specs: SystemSpec, name: str,
                 time: Quantity, rf_waveform: Quantity,
                 frequency_offset: Quantity, phase_offset: Quantity,
                 bandwidth: Quantity,
                 rf_events: Tuple[Quantity, Quantity],
                 snap_to_raster: bool = False):

        self._rf = (time.to("ms"), rf_waveform.to("uT"))
        self.rf_events = (rf_events[0].to("ms"), rf_events[1].to("degree"))

        self.phase_offset = phase_offset.to("rad")
        self.frequency_offset = frequency_offset.to("Hz")
        self.bandwidth = bandwidth.to("kHz")
        super().__init__(system_specs, name, snap_to_raster)

    @property
    def tmin(self) -> Quantity:
        """ Returns the minimum time of the RF definition """
        return self._rf[0][0]

    @property
    def tmax(self) -> Quantity:
        """ Returns the maximum time of the RF definition """
        return self._rf[0][-1]

    def validate(self, system_specs: SystemSpec):
        """ Validates if the contained rf-definition is valid for the given system-
                specifications"""
        t, wf = self._rf
        float_steps = t.m_as("ms") / system_specs.rf_raster_time.m_as("ms")
        n_steps = np.around(float_steps)
        ongrid = np.allclose(n_steps, float_steps, rtol=1e-6)
        if not all([ongrid]):
            raise cmrseq.err.BuildingBlockValidationError(f"RF definition invalid:\n"
                             f"\t - definition on grid: {ongrid}\n")

        if np.max(np.abs(wf)) > system_specs.rf_peak_power:
            raise cmrseq.err.BuildingBlockValidationError(f"RF definition invalid:\n"
                             f"\t - peak power exceeds system limits: {np.max(np.abs(wf))}\n")

        if not np.allclose([wf[0].m_as("uT"), wf[-1].m_as("uT")],
                           Quantity(0, "uT").m, atol=1e-3):
            start, end = [np.round(wf[i].m_as('uT'), decimals=3) for i in (0, -1)]
            raise cmrseq.err.BuildingBlockValidationError(f"RF definition invalid:\n",
                             f"\t - start/end of waveform != 0: {start}/{end}\n")


    @property
    def rf(self) -> (Quantity, Quantity):
        """ Returns the complex RF-amplitude shifted/modulated by the phase/frequency offsets """
        t, amplitude = self._rf
        t_zero_ref = t - t[0]
        complex_amplitude = np.array((amplitude.m_as("uT") + 1j * np.zeros_like(amplitude.m_as("uT"))))
        phase_per_time = (self.phase_offset.m_as("rad") +
                          2 * np.pi * self.frequency_offset.m_as("kHz") * t_zero_ref.m_as("ms"))
        complex_amplitude = complex_amplitude * np.exp(1j * phase_per_time)
        return t, Quantity(complex_amplitude, "uT")

    @rf.setter
    def rf(self, value: Tuple[Quantity, Quantity]):
        self._rf = value

    @property
    def isodelay(self) -> Quantity:
        """Approximates isodelay as the time interval between peak RF energy and end of pulse,
        neglecting the (small) nonlinear dependence on flip angle. This is necessary to correctly
        compute the required gradient area in slice-selective excitation.
        """
        time, waveform = self._rf
        return time[-1] - self.rf_events[0]

    @property
    def normalized_waveform(self) -> (np.ndarray, Quantity, np.ndarray, Quantity):
        """Computes the normalized waveform (scaling between -1, 1).

        :return: - Normalized amplitude between [-1, 1] [dimensionless] (flipped such that the
                    maximum normalized value is positive. Scaling with peak amplitude inverts the
                    shape again)
                 - Peak amplitude in uT
                 - Phase per timestep in rad
                 - Time raster definition points
        """
        t, amplitude = self._rf
        t_zero_ref = t - t[0]
        if amplitude.m_as("uT").dtype in [np.complex64, np.complex128]:
            phase = np.angle(amplitude.m_as("uT"))
            # The subtraction of offsets is not required to remove the phase
            # as the addition is only performed in the public property self.rf
            # phase = phase - self.phase_offset.m_as("rad")
            # phase -= (t_zero_ref * 2 * np.pi * self.frequency_offset).m_as("rad")
            amplitude = amplitude.m_as("uT") * np.exp(-1j * phase)
        else:
            phase = np.zeros(amplitude.shape, dtype=np.float64)
            amplitude = amplitude.m_as("uT")

        peak_amp_plus, peak_amp_minus = np.max(amplitude), np.min(amplitude)
        absolute_max_idx = np.argmax([np.abs(peak_amp_plus), np.abs(peak_amp_minus)])
        peak_amp = (peak_amp_plus, peak_amp_minus)[absolute_max_idx]
        normed_amp = np.divide(amplitude, peak_amp, out=np.zeros_like(amplitude),
                               where=(peak_amp != 0))
        return np.real(normed_amp), Quantity(peak_amp, "uT"), phase, t_zero_ref

    def shift(self, time_shift: Quantity) -> None:
        """Adds the time-shift to all rf definition points and the rf-center"""
        time_shift =  time_shift.to("ms")
        self._rf = (self._rf[0] + time_shift, self._rf[1])
        self.rf_events = (self.rf_events[0] + time_shift, self.rf_events[1])

    def flip(self, time_flip: Quantity = None):
        """Time reverses block by flipping about a given time point. If no
        time is specified, the rf center of this block is choosen."""
        if time_flip is None:
            time_flip = self.rf_events[0][0]
        self._rf = (np.flip(time_flip.to("ms") - self._rf[0], axis=0), np.flip(self._rf[1], axis=1))
        self.rf_events = (np.flip(time_flip.to("ms") - self.rf_events[0], axis=0),
                          np.flip(self.rf_events[1], axis=0))

    def scale_angle(self, factor: float):
        """Scales the contained waveform amplitude and corresponding rf_events by
        given factor. Resulting in scaled flip angles.
        """
        self.rf_events = (self.rf_events[0].to("ms"), self.rf_events[1].to("degree") * factor)
        self._rf = (self._rf[0], self._rf[1] * factor)

    def snap_to_raster(self, system_specs: SystemSpec):
        """Rounds the time-points and waveform to the nearest raster point. 
        Warning: When calling snap_to_raster the waveform points are simply rounded to their nearest neighbour if the difference is below the relative tolerance.
        Therefore this is not guaranteed to be precise anymore

        """
        
        warn("RF.snap_to_raster Warning: When calling snap_to_raster the waveform points are simply"
             "rounded to their nearest neighbour if the difference is below the relative tolerance."
             "Therefore this is not guaranteed to be precise anymore")

        t_rf = system_specs.time_to_raster(self._rf[0], "rf")
        self._rf = (t_rf.to("ms"), self._rf[1])


class SincRFPulse(RFPulse):
    """Defines a Sinc-RF pulse on a time grid with step length defined by system_specs. The
    window function used to temporally limit the waveform is given as:

    .. math::

        window = (1 - \\beta) + \\beta cos(2 \\pi n /N)

    where :math:`\\beta` is the specified apodization argument. If set to 0.5 the used window is a
    Hanning window resulting in 0 start and end. using 0.46 results in the use of a Hamming window.

    :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                        Values the flip-angle is stored as positive absolute plus a phase offset
                        of 180°
    :param duration: Quantity[Time] Total duration of the pulse
    :param time_bandwidth_product: float - Used to calculate the pulse-bandwidth. For a
                Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                half central-lobe-width
    :param center: float [0, 1] factor to compute the pulse center relative to duration
    :param delay: Adds temporal offset to pulse
    :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
    :param frequency_offset: Frequency offset in Hz in rotating frame ()
    :param phase_offset: Phase offset in rad.
    :param name: semantic label of the building block
    """
    # pylint: disable=R0913, R0914
    def __init__(self,
                 system_specs: SystemSpec,
                 duration: Quantity,
                 flip_angle: Quantity = Quantity(np.pi, "rad"),
                 time_bandwidth_product: float = 3.,
                 center: float = 0.5,
                 delay: Quantity = Quantity(0., "ms"),
                 apodization: float = 0.5,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "sinc_rf"):
        """ Defines a Sinc-RF pulse on a time grid with step length defined by system_specs.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                            Values the flip-angle is stored as positive absolute plus a phase offset
                            of 180°
        :param duration: Quantity[Time] Total duration of the pulse
        :param time_bandwidth_product: float - Used to calculate the pulse-bandwidth. For a
                    Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                    half central-lobe-width
        :param center: float [0, 1] factor to compute the pulse center relative to duration
        :param delay:
        :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """

        if flip_angle < Quantity(0, "rad"):
            phase_offset += Quantity(np.pi, "rad")
            flip_angle = -flip_angle

        time_points, unit_wf = self.get_unit_waveform(
                                            raster_time=system_specs.rf_raster_time,
                                            time_bandwidth_product=time_bandwidth_product,
                                            duration=duration, apodization=apodization,
                                            center=center)

        # For Sinc-Pulse this t*bw/duration corresponds to half central lobe width
        bandwidth = Quantity(time_bandwidth_product / duration.to("ms"), "1/ms")

        unit_flip_angle = np.sum((unit_wf[1:] + unit_wf[:-1]) / 2) * system_specs.rf_raster_time.to("ms")\
                          * system_specs.gamma_rad.to("rad/mT/ms")

        amplitude = unit_wf * flip_angle.to("rad") / unit_flip_angle

        super().__init__(system_specs=system_specs, name=name,
                         time=time_points + delay, rf_waveform=amplitude,
                         frequency_offset=frequency_offset, phase_offset=phase_offset,
                         rf_events=(center * duration + delay, flip_angle),
                         bandwidth=bandwidth, snap_to_raster=False)

    @staticmethod
    def get_unit_waveform(raster_time: Quantity, time_bandwidth_product: float,
                          duration: Quantity, apodization: float, center: float) -> Quantity:
        """ Constructs the sinc-pulse waveform according to:

        .. math::

            wf = (1 - \\Gamma + \\Gamma cos(2\pi / \\Delta * t)) * sinc(tbw/\\Delta t)

        where

        .. math::
            \\Gamma     :& apodization (typically 0.46) \\\\
            \\Delta     :& Pulse duration \\\\
            tbw        :& Time-bandwidth-product \\\\
            t          :& time on raster where center defines 0.


        """
        bandwidth = Quantity(time_bandwidth_product / duration.m_as("ms"), "1/ms")
        n_steps = np.around(duration.m_as("ms") / raster_time.m_as("ms"))
        time_points = Quantity(np.arange(0., n_steps+1, 1) * raster_time.m_as("ms"), "ms")
        time_rel_center = time_points.to("ms") - (center * duration.to("ms"))
        window = (1 - apodization) + apodization * np.cos(2 * np.pi * np.arange(-n_steps//2, n_steps//2+1, 1) / n_steps)
        unit_wf = np.sinc((bandwidth.to("1/ms") * time_rel_center).m_as("dimensionless")) * window
        unit_wf -= unit_wf[0]
        return time_points, unit_wf

    @classmethod
    def from_shortest(cls, system_specs: SystemSpec, flip_angle: Quantity,
                      time_bandwidth_product: float = 3., center: float = 0.5,
                      delay: Quantity = Quantity(0., "ms"),
                      apodization: float = 0.5,
                      frequency_offset: Quantity = Quantity(0., "Hz"),
                      phase_offset: Quantity = Quantity(0., "rad"),
                      name: str = "sinc_rf"):
        """Creates the shortest Sinc RF pulse for specified arguments.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the Sinc Pulse. For negative
                            Values the flip-angle is stored as positive absolute plus a phase offset
                            of 180°
        :param time_bandwidth_product: float - Used to calculate the pulse-bandwidth. For a
                    Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                    half central-lobe-width
        :param center: float [0, 1] factor to compute the pulse center relative to duration
        :param delay:
        :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """
        durations = Quantity(np.linspace(0.1, 1.5, 2), "ms")
        fas = []
        for dur in durations:
            _, unit_wf = cls.get_unit_waveform(raster_time=system_specs.rf_raster_time,
                                               time_bandwidth_product=time_bandwidth_product,
                                               duration=dur, apodization=apodization,
                                               center=center)
            max_wf =  unit_wf * system_specs.rf_peak_power.to("uT")
            fa = np.sum((max_wf[1:] + max_wf[:-1]) / 2 * system_specs.rf_raster_time.to("ms"))
            fa *= system_specs.gamma_rad.to("rad/mT/ms")
            fas.append(fa.m_as("degree"))
        slope = Quantity(np.diff(durations.m_as("ms")) / np.diff(fas), "ms/degree")[0]
        target_duration = system_specs.time_to_raster(np.abs(flip_angle) * slope, "rf")

        return cls(system_specs, duration=target_duration,
                   flip_angle=flip_angle, time_bandwidth_product=time_bandwidth_product,
                   center=center, delay=delay, apodization=apodization,
                   frequency_offset=frequency_offset, phase_offset=phase_offset, name=name)


class HardRFPulse(RFPulse):
    """ Defines a constant (hard) RF pulse on a time grid with step length defined by system_specs.

    :param flip_angle: Quantity[Angle] Desired Flip angle of the RF Pulse. For negative
                        Values the flip-angle is stored as positive absolute plus a phase offset
                        of 180°
    :param duration: Quantity[Time] Total duration of the pulse
    :param delay: Leading time to RR start
    :param frequency_offset: Frequency offset in Hz in rotating frame ()
    :param phase_offset: Phase offset in rad.
    :param name: defaults to 'hard_rf'
    """
    # pylint: disable=R0913, R0914
    def __init__(self,
                 system_specs: SystemSpec,
                 flip_angle: Quantity = Quantity(np.pi, "rad"),
                 duration: Quantity = Quantity(1., "ms"),
                 delay: Quantity = Quantity(0., "ms"),
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "hard_rf"):

        if flip_angle < Quantity(0, "rad"):
            phase_offset += Quantity(np.pi, "rad")
            flip_angle = -flip_angle

        raster_time = system_specs.rf_raster_time.to("ms")

        # If duration is too short, we can not create a pulse due to raster time
        if duration<2*system_specs.rf_raster_time:
            duration = 2 *system_specs.rf_raster_time


        # estimate number of steps at the plateau (if any)
        n_steps = np.around((duration.m_as("ms")-2*system_specs.rf_raster_time.m_as("ms"))
                            / raster_time.m_as("ms"))

        # estimate amplitude
        amplitude = (flip_angle / system_specs.gamma_rad / (raster_time * (n_steps + 1))).to('mT')

        # First case, we are below max B1 and have triangular pulse
        if n_steps<1 and amplitude<=system_specs.rf_peak_power:
            time_points = Quantity(np.array([0,1,2]) * raster_time.m_as("ms"), "ms")
            amplitude = amplitude*np.array([0,1,0])
        # Second case, still below max B1 but now have trapezoidal pulse
        elif amplitude<=system_specs.rf_peak_power:
            time_points = Quantity(np.array([0,1,n_steps+1,n_steps+2]) * raster_time.m_as("ms"),
                                   "ms")
            amplitude = amplitude * np.array([0, 1, 1, 0])
        # Third case, need to recalculate duration at max B1
        else:
            n_steps = np.ceil((flip_angle / system_specs.gamma_rad /
                               raster_time / system_specs.rf_peak_power-1).m_as("dimensionless"))
            time_points = Quantity(np.array([0, 1, n_steps + 1, n_steps + 2])
                                   * raster_time.m_as("ms"), "ms")
            amplitude = (flip_angle / system_specs.gamma_rad /
                         (raster_time * (n_steps + 1))).to('mT') * np.array([0, 1, 1, 0])

        super().__init__(system_specs=system_specs, name=name,
                         time=time_points + delay, rf_waveform=amplitude,
                         frequency_offset=frequency_offset, phase_offset=phase_offset,
                         rf_events=(duration/2 + delay, flip_angle),
                         bandwidth=0.5/duration, snap_to_raster=False)

class GaussRFPulse(RFPulse):
    """Defines a Gauss-RF pulse on a time grid with step length defined by system_specs. The
    window function used to temporally limit the waveform is given as:

    .. math::

        window = (1 - \\beta) + \\beta cos(2 \\pi n /N)

    where :math:`\\beta` is the specified apodization argument. If set to 0.5 the used window is a
    Hanning window resulting in 0 start and end. using 0.46 results in the use of a Hamming window.

    :param flip_angle: Quantity[Angle] Desired Flip angle of the Gauss Pulse. For negative
                        Values the flip-angle is stored as positive absolute plus a phase offset
                        of 180°
    :param duration: Quantity[Time] Total duration of the pulse
    :param time_bandwidth_product: float - Used to calculate the pulse-bandwidth. For a
                Gauss-Pulse bw = time_bandwidth_product/duration corresponds to the
                half central-lobe-width
    :param center: float [0, 1] factor to compute the pulse center relative to duration
    :param delay: Adds temporal offset to pulse
    :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
    :param frequency_offset: Frequency offset in Hz in rotating frame ()
    :param phase_offset: Phase offset in rad.
    :param name: semantic label of the building block
    """
    def __init__(self, system_specs: 'SystemSpec',
                 duration: Quantity,
                 flip_angle: Quantity = Quantity(np.pi, "rad"),
                 time_bandwidth_product: float = 4.,
                 center: float = 0.5,
                 delay: Quantity = Quantity(0., "ms"),
                 apodization: float = 0.5,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 name: str = "gauss_rf"):

        if flip_angle < Quantity(0, "rad"):
            phase_offset += Quantity(np.pi, "rad")
            flip_angle = -flip_angle

        time_points, unit_wf = self.get_unit_waveform(
                                            raster_time=system_specs.rf_raster_time,
                                            time_bandwidth_product=time_bandwidth_product,
                                            duration=duration, apodization=apodization,
                                            center=center)

        # For Sinc-Pulse this t*bw/duration corresponds to half central lobe width
        bandwidth = Quantity(time_bandwidth_product / duration.to("ms"), "1/ms")

        unit_flip_angle = (np.sum((unit_wf[1:] + unit_wf[:-1]) / 2)
                           * system_specs.rf_raster_time.to("ms")
                           * system_specs.gamma_rad.to("rad/mT/ms"))
        amplitude = unit_wf * flip_angle.to("rad") / unit_flip_angle

        super().__init__(system_specs=system_specs, name=name,
                         time=time_points + delay, rf_waveform=amplitude,
                         frequency_offset=frequency_offset, phase_offset=phase_offset,
                         rf_events=(center * duration + delay, flip_angle),
                         bandwidth=bandwidth, snap_to_raster=False)
    @staticmethod
    def get_unit_waveform(raster_time: Quantity, time_bandwidth_product: float,
                          duration: Quantity, apodization: float,
                          center: float) -> Quantity:
        """ Constructs a normalized Gaussian pulse waveform according to:

        .. math::

            wf = (1 - \Gamma + \Gamma cos(2\pi / \Delta * t)) * exp(-(tbw/\Delta t)^2)

        where

        .. math::
            \Gamma     :& apodization (typically 0.46) \\\\
            \Delta     :& Pulse duration \\\\
            tbw        :& Time-bandwidth-product \\\\
            t          :& time on raster where center defines 0.


        """
        bandwidth = Quantity(time_bandwidth_product / duration.m_as("ms"), "1/ms")
        n_steps = np.around(duration.m_as("ms") / raster_time.m_as("ms"))
        time_points = Quantity(np.arange(0., n_steps + 1, 1)
                               * raster_time.m_as("ms"), "ms")
        time_rel_center = time_points.to("ms") - (center * duration.to("ms"))
        window = (1 - apodization) + apodization * np.cos(
            2 * np.pi * np.arange(-n_steps // 2, n_steps // 2 + 1, 1) / n_steps)
        unit_wf = np.exp(-(bandwidth.to("1/ms") * time_rel_center).m_as("dimensionless")**2)
        unit_wf *= window
        unit_wf -= unit_wf[0]
        return time_points, unit_wf

    @classmethod
    def from_shortest(cls, system_specs: SystemSpec, flip_angle: Quantity,
                      time_bandwidth_product: float = 3., center: float = 0.5,
                      delay: Quantity = Quantity(0., "ms"),
                      apodization: float = 0.5,
                      frequency_offset: Quantity = Quantity(0., "Hz"),
                      phase_offset: Quantity = Quantity(0., "rad"),
                      name: str = "sinc_rf"):
        """Creates the shortest Gauss RF pulse for specified arguments.

        :param flip_angle: Quantity[Angle] Desired Flip angle of the Gauss Pulse. For negative
                           values the flip-angle is stored as positive absolute plus a phase offset
                           of 180°
        :param time_bandwidth_product: float - Used to calculate the pulse-bandwidth. For a
                    Sinc-Pulse bw = time_bandwidth_product/duration corresponds to the
                    half central-lobe-width
        :param center: float [0, 1] factor to compute the pulse center relative to duration
        :param delay:
        :param apodization: float from interval [0, 1] used to calculate cosine-apodization window
        :param frequency_offset: Frequency offset in Hz in rotating frame ()
        :param phase_offset: Phase offset in rad.
        :param name:
        """
        durations = Quantity(np.linspace(0.1, 1.5, 2), "ms")
        fas = []
        for dur in durations:
            _, unit_wf = cls.get_unit_waveform(raster_time=system_specs.rf_raster_time,
                                               time_bandwidth_product=time_bandwidth_product,
                                               duration=dur, apodization=apodization,
                                               center=center)
            max_wf = unit_wf * system_specs.rf_peak_power.to("uT")
            fa = np.sum((max_wf[1:] + max_wf[:-1]) / 2 * system_specs.rf_raster_time.to("ms"))
            fa *= system_specs.gamma_rad.to("rad/mT/ms")
            fas.append(fa.m_as("degree"))
        slope = Quantity(np.diff(durations.m_as("ms")) / np.diff(fas), "ms/degree")[0]
        target_duration = system_specs.time_to_raster(np.abs(flip_angle) * slope, "rf")

        return cls(system_specs, duration=target_duration,
                   flip_angle=flip_angle, time_bandwidth_product=time_bandwidth_product,
                   center=center, delay=delay, apodization=apodization,
                   frequency_offset=frequency_offset, phase_offset=phase_offset, name=name)

class ArbitraryRFPulse(RFPulse):
    """ Wrapper for arbitrary rf shapes, to adhere to building block concept.
    The gridding is assumed to be on raster time and **not** shifted by half
    a raster time. This shift (useful for simulations) can be incorporated when
    calling the gridding function of the sequence.

    The waveform is assumed to start and end with values of 0 uT. If the given waveform does not
    adhere to that definition, the arrays are padded.

    The rf-center (time-point of effective excitation) is estimated from pulse maximum.

    If not specified, the bandwidth of the given waveform is estimated by using the full width
    at half maximum of the power-spectrum.

      .. warning::

        For very long pulses, the estimation of bandwidth might not be reasonable anymore, due to
        relaxation.


    :param system_specs: SystemSpec instance
    :param time_points: Shape (#steps)
    :param waveform: Shape (#steps) in uT as complex array
    :param bandwidth: In Hz. If not specified, the bandwidth is estimated from the spectrum as
                 full-width-half-maximum.
    :param frequency_offset: Linear phase evolution, which is added to the complex when calling
                    the self.rf property
    :param phase_offset: Phase offset, which is added to the complex waveform when calling the
                    self.rf property
    :param snap_to_raster: If true waveform is rounded to raster time
    :param name: defaults to 'arbitrary_rf'
    """
    def __init__(self, system_specs: SystemSpec,
                 time_points: Quantity,
                 waveform: Quantity,
                 delay: Quantity = Quantity(0., "ms"),
                 bandwidth: Quantity = None,
                 frequency_offset: Quantity = Quantity(0., "Hz"),
                 phase_offset: Quantity = Quantity(0., "rad"),
                 snap_to_raster: bool = False,
                 name: str = "arbitrary_rf"):

        if not np.isclose(waveform[0].m_as("uT"), 0., atol=1e-3):
            time_points = np.concatenate([[time_points[0] - system_specs.rf_raster_time],
                                           time_points], axis=0)
            waveform = np.concatenate([[Quantity(0., "uT")], waveform], axis=0)

        if not np.isclose(waveform[-1].m_as("uT"), 0., atol=1e-3):
            time_points = np.concatenate([time_points,
                                          [time_points[-1] + system_specs.rf_raster_time]], axis=0)
            waveform = np.concatenate([waveform, [Quantity(0., "uT")]], axis=0)

        _, center_index = _calculate_rf_center(time=time_points.to("ms"),
                                                         rf_waveform=waveform)
        flip_angle = _calculate_flipangle(time=time_points, rf_waveform=waveform,
                                               gamma_rad=system_specs.gamma_rad)

        ## This is a weird case that can occur on loading other format definitions
        if np.allclose(waveform.m_as("uT"), 0., atol=1e-3):
            bandwidth = Quantity(0, "Hz")

        if bandwidth is None:
            _, _, bandwidth = _calculate_bandwidth(time=time_points, rf_waveform=waveform,
                                                        cut_off_percent=0.5,
                                                        min_frequency_resolution=Quantity(10, "Hz"))

        super().__init__(system_specs, name, frequency_offset=frequency_offset,
                         time=time_points.to("ms") + delay, rf_waveform=waveform.to("mT"),
                         phase_offset=phase_offset, bandwidth=bandwidth,
                         rf_events=(time_points[center_index] + delay, flip_angle.to("rad")),
                         snap_to_raster=snap_to_raster)

class AdiabaticRFPulse(RFPulse):
    """Class for implementation of adiabatic pulses, hence including amplitude and
    frequency modulation.

    The phase offset and frequency offset attributes are used to compute the complex rf-waveform
    representation using the `RFPulse.rf` - property.

    :param system_specs: SystemSpecs object
    :param name: string to name the building block
    :param time: (# points) time-points defining the waveform duration
    :param rf_waveform: (#points) rf-amplitude
    :param phase_offset: Phase in radians, Used to compute the complex rf-waveform
    :param frequency_offset: Used to compute the linear phase modulation due to a frequency offset
                                of the complex rf-waveform
    :param rf_events: tuple containing (event, flip angle)
    :param phase_modulation: Quantity containing a variable phase modulation for all points
                                 in the specified rf_waveform
    :param snap_to_raster: If true waveform is rounded to raster time
    """
    #: Variable RF phase modulation of the complex waveform in (rad)
    phase_modulation: Quantity

    def __init__(self, system_specs: 'cmrseq.SystemSpec',
                 name: str, time: Quantity, rf_waveform: Quantity,
                 frequency_offset: Quantity, phase_offset: Quantity,
                 bandwidth: Quantity,
                 rf_events: Tuple[Quantity, Quantity],
                 phase_modulation: Quantity,
                 snap_to_raster: bool = False):
        super().__init__(system_specs, name=name, time=time,
                         rf_waveform=rf_waveform,
                         frequency_offset=frequency_offset,
                         phase_offset=phase_offset, bandwidth=bandwidth,
                         rf_events=rf_events, snap_to_raster=snap_to_raster)
        self.phase_modulation = phase_modulation

    @property
    def rf(self) -> (Quantity, Quantity):
        """ Returns the complex RF-amplitude shifted/modulated by the phase/frequency offsets """
        t, amplitude = self._rf
        t_zero_ref = t - t[0]
        complex_amplitude = amplitude.m_as("uT") + 1j * np.zeros_like(amplitude.m_as("uT"))
        phase_modulation = self.phase_modulation.m_as("rad") + self.phase_offset.m_as("rad")
        phase_modulation += 2 * np.pi * self.frequency_offset.m_as("kHz") * t_zero_ref.m_as("ms")
        complex_amplitude = complex_amplitude * np.exp(1j * phase_modulation)
        return t, Quantity(complex_amplitude, "uT")

    @classmethod
    def from_bir4(cls, system_specs: 'cmrseq.SystemSpec',
                  duration: Quantity,
                  flip_angle: Quantity,
                  beta: float,
                  kappa: float,
                  b1_amplitude: Quantity,
                  phase_offset: Quantity = Quantity(0, "rad"),
                  delay: Quantity = Quantity(0, "ms"),
                  d0: float = 1) -> 'AdiabaticRFPulse':
        """Constructs an adiabatic B_1-insensitive rotation pulse by wrapping the sigpy
        implementation given at.

        https://sigpy.readthedocs.io/en/latest/generated/sigpy.mri.rf.adiabatic.bir4.html

        :raises: SequenceArgumentError - if duration is not a 4x multiple of RF-raster time

        .. Dropdown:: Overview
            :animate: fade-in-slide-down
            :icon: graph
            :color: secondary

            ..  figure:: ../_static/api/core_rf_BIR4_highlighting.png
                :class: with-shadow

                a) Amplitude modulation and b) frequency modulation of the BIR-4 pulse.
                c) Real and d) imaginary part of the resulting complex waveform. e) Flip
                angle as function of B1-max for on-resonant spins. f) Difference to target
                flip-angle as function of B1-max and off-resonance.


        .. Dropdown:: Flip angle dependency B1 / Off-resonance on parameters
            :animate: fade-in-slide-down
            :icon: graph
            :color: secondary

            ..  figure:: ../_static/api/core_rf_BIR4_beta_dependency.png
                :class: with-shadow

                Difference to target flip-angle for varying values of math:`beta`

            ..  figure:: ../_static/api/core_rf_BIR4_kappa_dependency.png
                :class: with-shadow

                Difference to target flip-angle for varying values of :math:`kappa`

            ..  figure:: ../_static/api/core_rf_BIR4_dw0_dependency.png
                :class: with-shadow

                Difference to target flip-angle for varying values of :math:`\\delta \omega_0`

        :param system_specs: SystemSpecification object
        :param duration: Total duration of the pulse
        :param flip_angle: Expected maximal flip-angle
        :param beta: dimensionless AM constant, determines how well adiabatic condition is met
        :param kappa: dimensionless FM constant, determines how well adiabatic condition is met
        :param phase_offset: Phase in radians, Used to compute the complex rf-waveform
        :param b1_amplitude: B1-max scaling in uT
        :param delay: Shift of start point
        :param d0:
        :return: AdiabaticRFPulse
        """
        import sigpy.mri.rf as sigpy_rf

        n_samples = (duration / system_specs.rf_raster_time).m_as("dimensionless") - 2
        if abs(int(n_samples) - n_samples) > 1e-6 or int(n_samples) % 4 != 0:
            raise cmrseq.err.SequenceArgumentError(message="Duration + 2 raster time not 4x multiple of RF-raster-time",
                                                   argument='duration')
        n_samples = int(n_samples)

        dw0 = (d0 * np.pi / duration).m_as("1/ms")
        # Call sigpy and convert modulation into rf-waveform
        amp_modulation, freq_modulation = sigpy_rf.adiabatic.bir4(n_samples, beta, kappa,
                                                                  flip_angle.m_as("rad"), dw0)
        rf_waveform = np.pad(amp_modulation, (1, 1)) * b1_amplitude
        phase_modulation = Quantity(np.cumsum(freq_modulation), "kHz") * system_specs.rf_raster_time
        phase_modulation = np.pad(phase_modulation, (1, 1))
        time = np.arange(0, n_samples + 2) * system_specs.rf_raster_time + delay
        rf_center, _ = _calculate_rf_center(time, rf_waveform)

        rf_events = (rf_center + delay, flip_angle)
        obj = cls(system_specs, name="rf_adiabatic_bir4", time=time, rf_waveform=rf_waveform,
                  phase_offset=phase_offset, frequency_offset=Quantity(0, "Hz"),
                  bandwidth=Quantity(0, "Hz"), rf_events=rf_events,
                  phase_modulation=phase_modulation)
        return obj

    @classmethod
    def from_hyperbolic_secant(cls, system_specs: 'cmrseq.SystemSpec',
                               duration: Quantity,
                               beta: Quantity, mu: float,
                               flip_angle: Quantity = None,
                               max_amplitude: Quantity = None,
                               phase_offset: Quantity = Quantity(0, "rad"),
                               frequency_offset: Quantity = Quantity(0, "Hz"),
                               delay: Quantity = Quantity(0, "ms")) -> 'AdiabaticRFPulse':
        """Constructs an adiabatic hyperbolic secant pulse, by either using target flip-angle or
        a peak rf amplitude. If

        https://sigpy.readthedocs.io/en/latest/generated/sigpy.mri.rf.adiabatic.hypsec.html

        For more information on how the parameters relate to the inversion profile see following
        presentation:
        https://labs.dgsom.ucla.edu/mrrl/files/view/m229-2021/M229_Lecture5_Adiabatic_Pulses.pdf


        Computations for relation of max amplitude and flip-angle as well as bandwidth
        is given in the appendix of

         Wastling SJ, Barker GJ. Designing hyperbolic secant excitation pulses to reduce signal
         dropout in gradient-echo echo-planar imaging.
         Magn. Reson. Med. 2015;74:661–672 doi: 10.1002/MRM.25444.

        .. Dropdown:: Example Plots
            :animate: fade-in-slide-down
            :icon: graph
            :color: secondary

            .. image:: ../_static/api/core_rf_adiabatic_hypsec.png

        :raises: SequenceArgumentError - if duration is not on RF-raster time

        :param system_specs: SystemSpecification object
        :param duration: Total duration of the pulse
        :param beta: modulation parameter in rad/s, which determines how well adiabatic
                     condition is met, with usual values of multiple kHz
        :param mu: :math:`\\beta\\mu` is scaling the frequency modulation with :math:`2 < \\mu < 8` being
                reasonable values
        :param flip_angle: If specified, the max amplitude is computed to achieve the target flip
                angle as stated in (doi: 10.1002/MRM.25444).
        :param max_amplitude: Peak RF amplitude. This does not influence the flip-angle if
                adiabaticity is given (:math:`B_{1max} >> (\\beta\\sqrt{\\mu} / \\gamma)`)
                but refines the inversion profile as described in slide 33 of the reference stated
                above. In this case the spectral RF bandwidth is given :math:`\\beta\\mu`
        :param phase_offset: Phase in radians, Used to compute the complex rf-waveform
        :param frequency_offset: Linear phase contribution, that is added when computing the
                complex-valued RF-waveform in RFPulse.rf
        :param delay: Shift of start point
        :return: AdiabaticRFPulse
        """

        if (flip_angle is None and max_amplitude is None or
                not (flip_angle is None or max_amplitude is None)):
            raise cmrseq.err.BuildingBlockArgumentError(
                message="Exactly one of the arguments mus be specified",
                argument='flip_angle/max_amplitude',
                class_name="AdiabaticRFPulse")

        if beta.units != Quantity(1, "rad/s").units:
            raise cmrseq.err.BuildingBlockArgumentError("Please explicitly specify in rad/s to "
                                                        "prevent conversion errors", argument='beta',
                                                        class_name="AdiabaticRFPulse")

        if max_amplitude is None:
            # Using eq. 17 of stated reference
            # Note: _term_2
            _alpha = flip_angle.m_as("rad")
            _term_0 = math.pi * mu / 2
            _term_1 = math.cos(_alpha) * math.cosh(_term_0) ** 2 + math.sinh(_term_0) ** 2
            _term_2 = (cmath.acos(_term_1) / math.pi) ** 2 + mu ** 2
            max_amplitude = (beta / system_specs.gamma_rad * math.sqrt(_term_2.real)).to("uT")
            del _term_0, _term_1, _term_2, _alpha

        n_samples = (duration / system_specs.rf_raster_time).m_as("dimensionless") - 2
        if abs(int(n_samples) - n_samples) > 1e-6:
            raise cmrseq.err.BuildingBlockArgumentError(message="Duration not on RF-raster-time",
                                                        argument='duration',
                                                        class_name="AdiabaticRFPulse")

        n_samples = int(n_samples)
        t = np.arange(- n_samples // 2, n_samples // 2) / n_samples * duration.to("ms")
        rf_waveform = max_amplitude / np.cosh(beta * t)
        frequency_modulation = - mu * beta * np.tanh(beta * t)
        phase_modulation = np.cumsum(frequency_modulation).to("rad/ms") * system_specs.rf_raster_time

        rf_waveform = np.pad(rf_waveform, (1, 1))
        phase_modulation = np.pad(phase_modulation, (1, 1))
        time = np.arange(0, n_samples + 2) * system_specs.rf_raster_time + delay
        rf_center, _ = _calculate_rf_center(time, rf_waveform)

        if flip_angle is None:
            bandwidth = (beta * mu).to("Hz")
            rf_events = (rf_center + delay, Quantity(180, "degree"))
        else:
            # Using eq. 22 in stated reference
            _alpha = flip_angle.m_as("rad")
            _arg_term = math.sqrt(3 + math.cos(_alpha)**2) / 2
            _arg_num = math.cosh(np.pi * mu) * (math.cos(_alpha) -_arg_term) + math.cos(_alpha) - 1
            _arg_den = _arg_term - 1
            bandwidth = beta / np.pi**2 * math.acosh(_arg_num / _arg_den)
            rf_events = (rf_center + delay, flip_angle.to("degree"))

        obj = cls(system_specs, name="rf_adiabatic_hypsec", time=time, rf_waveform=rf_waveform,
                  phase_offset=phase_offset, frequency_offset=frequency_offset,
                  bandwidth=bandwidth, rf_events=rf_events,
                  phase_modulation=phase_modulation)
        return obj

class SLRPulse(RFPulse):
    """Bundles the construction of RF pulses using the Shinnar-Le Roux as
    implemented by the sigpy package. For more details on suitable argument
    values, refer to the following publication:

     Pauly, J., Le Roux, Patrick., Nishimura, D., and Macovski, A.(1991).
     ‘Parameter Relations for the Shinnar-LeRoux Selective Excitation Pulse Design Algorithm’.
     IEEE Transactions on Medical Imaging, Vol 10, No 1, 53-65.

    https://sigpy.readthedocs.io/en/latest/generated/sigpy.mri.rf.slr.dzrf.html


    :param system_specs:
    :param flip_angle:
    :param pulse_duration:
    :param time_bandwidth_product:
    :param pulse_type: Allowed values ["small_tip", "excitation", "se_refocus", "inversion",
                    "saturation"]
    :param filter_type: Allowed values ["sinc", "pm_equal_ripple", "min_phase", "max_phase",
                                       "least_squares"]
    :param passband_ripple: Allowed ripple amplitude inside the pass-band in percent
                        (within slice profile)
    :param stopband_ripple: Allowed ripple amplitude outside the pass-band in percent
                        (determines side-band excitation signal).
    :param phase_offset: Offset in radians, that is added when computing the complex-valued
                         RF-waveform in RFPulse.rf
    :param frequency_offset: Linear phase contribution, that is added when computing the
                            complex-valued RF-waveform in RFPulse.rf
    :param cancel_alpha_phs: For ‘excitation’ pulses, absorb the alpha phase profile from
                        beta’s profile, so they cancel for a flatter total phase

    """
    # TODO: Add short conceptual explanations and application to filter-types?
    def __init__(self, system_specs: Quantity, flip_angle: Quantity, pulse_duration: Quantity,
                 time_bandwidth_product: float, pulse_type: str, filter_type: str,
                 passband_ripple: float = 0.01, stopband_ripple: float = 0.01,
                 phase_offset: Quantity = Quantity(0, "rad"),
                 frequency_offset: Quantity = Quantity(0, "Hz"),
                 delay: Quantity = Quantity(0., "ms"),
                 cancel_alpha_phs: bool = False):
        import sigpy.mri.rf as sigpy_rf

        pulse_type_lu = {"small_tip": "st", "excitation": "ex", "se_refocus":"se",
                          "inversion": "inv", "saturation":"sat"}
        if pulse_type not in pulse_type_lu.keys():
            raise cmrseq.err.BuildingBlockArgumentError(
                "Not in allowed values: " + '\n'.join(list(pulse_type_lu.keys())),
                argument='pulse_type', class_name='SLRPulse'
            )

        filter_type_lu = {"sinc": "ms", "pm_equal_ripple": "pm", "min_phase": "min",
                          "max_phase": "max", "least_squares": "ls"}
        if pulse_type not in pulse_type_lu.keys():
            raise cmrseq.err.BuildingBlockArgumentError(
                "Not in allowed values:" + '\n'.join(list(filter_type_lu.keys())),
                argument='filter_type', class_name='SLRPulse'
            )

        n_samples = (pulse_duration / system_specs.rf_raster_time).m_as("dimensionless")
        if abs(n_samples - int(n_samples)) > 1e-6:
            raise cmrseq.err.BuildingBlockArgumentError(
                "Not on RF raster-time", argument='pulse_duration', class_name='SLRPulse')
        n_samples = int(n_samples) - 2

        pulse = sigpy_rf.slr.dzrf(n_samples, time_bandwidth_product,
                                  pulse_type_lu[pulse_type],
                                  filter_type_lu[filter_type],
                                  passband_ripple, stopband_ripple,
                                  cancel_alpha_phs=cancel_alpha_phs)
        pulse = np.pad(pulse.real, (1, 1), mode="constant")

        if flip_angle is not None:
            flip_norm = Quantity(np.sum(pulse) * system_specs.rf_raster_time.m_as("s") * np.pi * 2,
                                 'rad')
            rf_waveform = Quantity((pulse * flip_angle / flip_norm).m_as("dimensionless"),
                                   "Hz") / system_specs.gamma
        else: # To get unscaled waveform
            rf_waveform = Quantity(pulse, "uT")
            flip_angle = Quantity(0, "degree")

        if np.max(rf_waveform.to("uT") > system_specs.rf_peak_power):
            raise cmrseq.err.BuildingBlockArgumentError(
                    message="Too short for given peak power limit",
                    argument="pulse_duration", class_name="SLRPulse")
        time = np.arange(0, n_samples+2) * system_specs.rf_raster_time
        rf_center, _ = _calculate_rf_center(time, rf_waveform)
        rf_events = (rf_center + delay, flip_angle)

        super().__init__(system_specs, name="slr_rf_pulse", time=time,
                         rf_waveform=rf_waveform, frequency_offset=frequency_offset,
                         phase_offset=phase_offset,
                         bandwidth=time_bandwidth_product / pulse_duration,
                         rf_events=rf_events, snap_to_raster=False)


def _calculate_flipangle(time: Quantity, rf_waveform: Quantity, gamma_rad: Quantity) \
        -> Quantity:
    """Numerical integration of the rf-waveform to obtain the flip-angle

    :param time: (#points, )
    :param rf_waveform: (#points, )
    :param gamma_rad: gyromagnetic ratio in units of radian
    :return: Quantity
    """
    flip_angle = gamma_rad * Quantity(
        np.trapz(rf_waveform.real.m_as("mT"), time.m_as("ms")),
        "mT ms")
    return flip_angle


def _calculate_bandwidth(time: Quantity, rf_waveform: Quantity, cut_off_percent: float,
                         min_frequency_resolution: Quantity) -> \
        Tuple[Quantity, Quantity, Quantity]:
    """ Calculates the RF-bandwidth for the given waveform as the spectral width at
    cut-off-percent.

    :param time: Quantity[Time] (#points,  ) Time centered around the RF-center
    :param rf_waveform: Quantity[Tesla]  (#points, )
    :param cut_off_percent:
    :param min_frequency_resolution: Minimal frequency target frequency resolution for spectrum
    :return: (frequency_grid, power_spectrum, bandwidth)
    """

    if np.abs(time[-1] - time[0]) > Quantity(20, "ms"):
        warn("RF.calculate_bandwidth: Long pulses > 20ms might not be accurately covered "
             "using the bandwidth estimation method for arbitrary RF pulses.")

    resample_dt = Quantity(1, "us")
    duration = (time[-1] - time[0]).to("us")
    n_grid_points = np.round((duration / resample_dt).m_as("dimensionless")).astype(int)

    # Padding the resampled temporal grid is done to achieve acceptable frequency resolution
    # for bandwidth calculation
    padding_factor = (1 / min_frequency_resolution / duration / 2).m_as("dimensionless")

    resampled_t_grid = Quantity(np.arange(
        -np.floor(n_grid_points * padding_factor).astype(int),
        np.ceil(n_grid_points * (padding_factor + 1)).astype(int)),
        "dimensionless") * resample_dt
    interpolated_wf = np.interp(xp=(time - time[0]).m_as("ms"), fp=rf_waveform.m_as("uT"),
                                x=resampled_t_grid.m_as("ms"), left=0, right=0)

    power_spectrum = np.abs(np.fft.fft(interpolated_wf))
    freq_grid = Quantity(np.fft.fftfreq(resampled_t_grid.shape[0], resample_dt.m_as("s")),
                         "Hz")

    ## For ascending order of the frequency grid
    sort_indices = np.argsort(freq_grid)
    freq_grid = freq_grid[sort_indices]
    power_spectrum = power_spectrum[sort_indices]

    peak = np.max(power_spectrum)

    above_threshold_indices = np.where(power_spectrum > peak * cut_off_percent)
    freq_band = freq_grid[above_threshold_indices].m_as("Hz")

    bandwidth = Quantity(freq_band[-1] - freq_band[0], "Hz")
    return freq_grid, power_spectrum, bandwidth


def _calculate_rf_center(time: Quantity, rf_waveform: Quantity) -> Tuple[Quantity, int]:
    """Calculates the time point of effective rotation for a given rf-waveform.

    Assumptions: - Mean of Peaks of absolute defines center
                 - Index on grid by rounding to nearest neighbor

    :param time: Quantity[Time] (#points,  )
    :param rf_waveform: Quantity[Tesla]  (#points, )
    :return: (Quantity, int) time-center (not on necessarily on grid) and integer to
                index the handed waveforms for a representation on grid
    """
    rf_max = np.max(np.abs(rf_waveform.m_as("uT")))
    peak_indices = np.where(np.abs(rf_waveform.m_as("uT")) >= rf_max * (1 - 1e-5))[0]
    time_center = np.mean([time.m_as("ms")[i] for i in peak_indices])
    center_index = np.round(np.mean(peak_indices)).astype(int)
    return Quantity(time_center, "ms"), center_index
