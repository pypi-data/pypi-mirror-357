"""
This file contains the definitions for several spin lock prepulses.
Each prepulse function takes three mandatory arguments: the system spec definition from
CMRseq (system_specs), the spin lock time (spin_lock_time), and the spin lock frequency
(spin_lock_frequency) of the prepulse. Furthermore, by entering a value for adc samples,
an ADC readout can be added during the prepulse, to visualize the signal progression during
the spin lock pulse.
"""

__all__ = ["simple", "rotary_echo", "composite", "balanced",
           "paired_self_compensated", "totally_balanced"]

import numpy as np
from pint import Quantity

import cmrseq


def simple(system_specs: cmrseq.SystemSpec, spin_lock_time: Quantity,
           spin_lock_frequency: Quantity, adc_samples: int = 0) -> cmrseq.Sequence:
    """Simple spin lock prepulse:

        90+x -> SL+y -> 90-x

    :param system_specs: SystemSpecification
    :param spin_lock_time: Quantity containing spin locking time
    :param spin_lock_frequency: Quantity containing spin locking frequency
    :param adc_samples: int containing the number of ADC samples
                        during the prepulse. If adc_samples=0,
                        no adc is integrated. Useful for debugging and
                        monitoring the signal during spin lock pulse.
    """
    pulse90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                           flip_angle=Quantity(90, 'degrees'),
                                           duration=Quantity(5., 'us'),
                                           frequency_offset=Quantity(0, 'Hz'),
                                           phase_offset=Quantity(0, 'rad'),
                                           delay=Quantity(0, "ms"),
                                           name="+90x")

    # calculate the "flip angle" from the SL frequency and SL time
    sl_flipangle = (spin_lock_frequency * spin_lock_time).to("degree")

    SLpulse = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                           flip_angle=sl_flipangle,
                                           duration=spin_lock_time,
                                           frequency_offset=Quantity(0, 'Hz'),
                                           phase_offset=Quantity(np.pi / 2, 'rad'),
                                           delay=pulse90.duration,
                                           name="SL+y")

    pulseneg90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                              flip_angle=Quantity(-90, 'degrees'),
                                              duration=Quantity(5., 'us'),
                                              frequency_offset=Quantity(0, 'Hz'),
                                              phase_offset=Quantity(0, 'rad'),
                                              delay=spin_lock_time + pulse90.duration,
                                              name="-90x")

    if adc_samples > 0:
        adc_duration = pulse90.duration + spin_lock_time + pulseneg90.duration
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(system_specs=system_specs,
                                                                num_samples=adc_samples,
                                                                duration=adc_duration)
        return cmrseq.Sequence([adc, pulse90, SLpulse, pulseneg90],
                               system_specs=system_specs)
    else:
        return cmrseq.Sequence([pulse90, SLpulse, pulseneg90],
                               system_specs=system_specs)


def rotary_echo(system_specs: cmrseq.SystemSpec, spin_lock_time: Quantity,
                spin_lock_frequency: Quantity, adc_samples: int = 0) -> cmrseq.Sequence:
    """Rotary echo spin lock prepulse

        90+x -> SL+y -> SL-y -> 90-x

    :param system_specs: SystemSpecification
    :param spin_lock_time: Quantity containing spin locking time
    :param spin_lock_frequency: Quantity containing spin locking frequency
    :param adc_samples: int containing the number of ADC samples
                        during the prepulse. If adc_samples=0,
                        no adc is integrated. Useful for debugging and
                        monitoring the signal during spin lock pulse.
    """
    pulse90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                           flip_angle=Quantity(90, 'degrees'),
                                           duration=Quantity(5., 'us'),
                                           frequency_offset=Quantity(0, 'Hz'),
                                           phase_offset=Quantity(0, 'rad'),
                                           delay=Quantity(0, "ms"),
                                           name="+90x")

    # calculate the "flip angle" from the SL frequency and SL time
    sl_flipangle = (spin_lock_frequency * spin_lock_time).to("degree")

    sl_pulse_1 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 2,
                                             duration=spin_lock_time / 2,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration,
                                             name="SL+y")

    sl_pulse_2 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 2,
                                             duration=spin_lock_time / 2,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(-np.pi / 2, 'rad'),
                                             delay=pulse90.duration + spin_lock_time / 2,
                                             name="SL-y")

    pulseneg90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                              flip_angle=Quantity(-90, 'degrees'),
                                              duration=Quantity(5., 'us'),
                                              frequency_offset=Quantity(0, 'Hz'),
                                              phase_offset=Quantity(0, 'rad'),
                                              delay=spin_lock_time + pulse90.duration,
                                              name="-90x")

    if adc_samples > 0:
        adc_duration = pulse90.duration + spin_lock_time + pulseneg90.duration
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(system_specs=system_specs,
                                                                num_samples=adc_samples,
                                                                duration=adc_duration)
        return cmrseq.Sequence([adc, pulse90, sl_pulse_1, sl_pulse_2, pulseneg90],
                               system_specs=system_specs)
    else:
        return cmrseq.Sequence([pulse90, sl_pulse_1, sl_pulse_2, pulseneg90],
                               system_specs=system_specs)


def composite(system_specs: cmrseq.SystemSpec, spin_lock_time: Quantity,
              spin_lock_frequency: Quantity, adc_samples: int = 0) -> cmrseq.Sequence:
    """Composite spin lock prepulse

        90+x -> SL+y -> 180+y -> SL-y -> 90-x

    :param system_specs: SystemSpecification
    :param spin_lock_time: Quantity containing spin locking time
    :param spin_lock_frequency: Quantity containing spin locking frequency
    :param adc_samples: int containing the number of ADC samples
                        during the prepulse. If adc_samples=0,
                        no adc is integrated. Useful for debugging and
                        monitoring the signal during spin lock pulse.
    """
    pulse90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                           flip_angle=Quantity(90, 'degrees'),
                                           duration=Quantity(5., 'us'),
                                           frequency_offset=Quantity(0, 'Hz'),
                                           phase_offset=Quantity(0, 'rad'),
                                           delay=Quantity(0, "ms"),
                                           name="+90x")

    pulse180y = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=Quantity(180, 'degrees'),
                                             duration=Quantity(5., 'us'),
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration + spin_lock_time / 2,
                                             name="+180y")

    pulseneg90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                              flip_angle=Quantity(-90, 'degrees'),
                                              duration=Quantity(5., 'us'),
                                              frequency_offset=Quantity(0, 'Hz'),
                                              phase_offset=Quantity(0, 'rad'),
                                              delay=(spin_lock_time + pulse90.duration
                                                     + pulse180y.duration),
                                              name="-90x")

    # calculate the "flip angle" from the SL frequency and SL time
    sl_flipangle = (spin_lock_frequency * spin_lock_time).to("degree")

    slpulse_1 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 2,
                                             duration=spin_lock_time / 2,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration,
                                             name="SL+y")

    sl_pulse_2 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 2,
                                             duration=spin_lock_time / 2,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(-np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time / 2
                                                    + pulse180y.duration),
                                             name="SL-y")

    if adc_samples > 0:
        adc_duration = pulse90.duration + spin_lock_time + pulse180y.duration + pulseneg90.duration
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(system_specs=system_specs,
                                                                num_samples=adc_samples,
                                                                duration=adc_duration)
        return cmrseq.Sequence([adc, pulse90, slpulse_1, pulse180y, sl_pulse_2, pulseneg90],
                               system_specs=system_specs)
    else:
        return cmrseq.Sequence([pulse90, slpulse_1, pulse180y, sl_pulse_2, pulseneg90],
                               system_specs=system_specs)


def balanced(system_specs: cmrseq.SystemSpec, spin_lock_time: Quantity,
             spin_lock_frequency: Quantity, adc_samples: int = 0) -> cmrseq.Sequence:
    """Balanced spin lock prepulse

            90+x -> SL+y -> 180+y -> SL-y -> 90-x

    :param system_specs: SystemSpecification
    :param spin_lock_time: Quantity containing spin locking time
    :param spin_lock_frequency: Quantity containing spin locking frequency
    :param adc_samples: int containing the number of ADC samples
                        during the prepulse. If adc_samples=0,
                        no adc is integrated. Useful for debugging and
                        monitoring the signal during spin lock pulse.
    """
    pulse90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                           flip_angle=Quantity(90, 'degrees'),
                                           duration=Quantity(5., 'us'),
                                           frequency_offset=Quantity(0, 'Hz'),
                                           phase_offset=Quantity(0, 'rad'),
                                           delay=Quantity(0, "ms"),
                                           name="+90x")

    pulse180y = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=Quantity(180, 'degrees'),
                                             duration=Quantity(5., 'us'),
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration + spin_lock_time / 4,
                                             name="+180y")

    pulseneg180y = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                                flip_angle=Quantity(180, 'degrees'),
                                                duration=Quantity(5., 'us'),
                                                frequency_offset=Quantity(0, 'Hz'),
                                                phase_offset=Quantity(-np.pi / 2, 'rad'),
                                                delay=(pulse90.duration + 3 * spin_lock_time / 4
                                                       + pulse180y.duration),
                                                name="-180y")

    pulseneg90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                              flip_angle=Quantity(-90, 'degrees'),
                                              duration=Quantity(5., 'us'),
                                              frequency_offset=Quantity(0, 'Hz'),
                                              phase_offset=Quantity(0, 'rad'),
                                              delay=(spin_lock_time + pulse90.duration +
                                                     pulse180y.duration + pulseneg180y.duration),
                                              name="-90x")

    # calculate the "flip angle" from the SL frequency and SL time
    sl_flipangle = (spin_lock_frequency * spin_lock_time).to("degree")

    slpulse_1 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration,
                                             name="SL+y")

    slpulse_2 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 2,
                                             duration=spin_lock_time / 2,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(-np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time / 4
                                                    + pulse180y.duration),
                                             name="SL-y")

    slpulse_3 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time * (3 / 4) +
                                                    pulse180y.duration + pulseneg180y.duration),
                                             name="SL+y")

    if adc_samples > 0:
        adc_duration = (pulse90.duration + spin_lock_time + pulse180y.duration +
                        pulseneg180y.duration + pulseneg90.duration)
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(
            system_specs=system_specs, num_samples=adc_samples,
            duration=adc_duration)
        return cmrseq.Sequence(
            [adc, pulse90, slpulse_1, pulse180y, slpulse_2, pulseneg180y, slpulse_3, pulseneg90],
            system_specs=system_specs)
    else:
        return cmrseq.Sequence(
            [pulse90, slpulse_1, pulse180y, slpulse_2, pulseneg180y, slpulse_3, pulseneg90],
            system_specs=system_specs)


def paired_self_compensated(system_specs: cmrseq.SystemSpec, spin_lock_time: Quantity,
                            spin_lock_frequency: Quantity, adc_samples: int = 0) -> cmrseq.Sequence:
    """Paired Self-Compensated (PSC) spin lock prepulse

        90+x -> SL+y -> SL-y -> 180+y -> SL+y -> SL-y -> 90-x

    :param system_specs: SystemSpecification
    :param spin_lock_time: Quantity containing spin locking time
    :param spin_lock_frequency: Quantity containing spin locking frequency
    :param adc_samples: int containing the number of ADC samples
                        during the prepulse. If adc_samples=0,
                        no adc is integrated. Useful for debugging and
                        monitoring the signal during spin lock pulse.
    """
    pulse90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                           flip_angle=Quantity(90, 'degrees'),
                                           duration=Quantity(5., 'us'),
                                           frequency_offset=Quantity(0, 'Hz'),
                                           phase_offset=Quantity(0, 'rad'),
                                           delay=Quantity(0, "ms"),
                                           name="+90x")

    pulse180y = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=Quantity(180, 'degrees'),
                                             duration=Quantity(5., 'us'),
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time / 2),
                                             name="+180y")

    pulseneg90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                              flip_angle=Quantity(-90, 'degrees'),
                                              duration=Quantity(5., 'us'),
                                              frequency_offset=Quantity(0, 'Hz'),
                                              phase_offset=Quantity(0, 'rad'),
                                              delay=(spin_lock_time + pulse90.duration
                                                     + pulse180y.duration),
                                              name="-90x")

    # calculate the "flip angle" from the SL frequency and SL time
    sl_flipangle = (spin_lock_frequency * spin_lock_time).to("degree")

    slpulse_1 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration,
                                             name="SL+y")

    slpulse_2 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(-np.pi / 2, 'rad'),
                                             delay=pulse90.duration + spin_lock_time / 4,
                                             name="SL-y")

    slpulse_3 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time / 2 +
                                                    pulse180y.duration),
                                             name="SL+y")

    slpulse_4 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(-np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time * (3 / 4)
                                                    + pulse180y.duration),
                                             name="SL-y")

    if adc_samples > 0:
        adc_duration = pulse90.duration + spin_lock_time + pulse180y.duration + pulseneg90.duration
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(system_specs=system_specs,
                                                                num_samples=adc_samples,
                                                                duration=adc_duration)
        return cmrseq.Sequence([adc, pulse90, slpulse_1, slpulse_2, pulse180y, slpulse_3,
                                slpulse_4, pulseneg90], system_specs=system_specs)
    else:
        return cmrseq.Sequence([pulse90, slpulse_1, slpulse_2, pulse180y, slpulse_3,
                                slpulse_4, pulseneg90], system_specs=system_specs)


def totally_balanced(system_specs: cmrseq.SystemSpec, spin_lock_time: Quantity,
                     spin_lock_frequency: Quantity, adc_samples: int = 0) -> cmrseq.Sequence:
    """Totally Balanced (TB) spin lock prepulse

        90+x -> SL+y -> 180+y -> SL-y -> SL+y -> 180-y -> SL-y -> 90-x

    :param system_specs: SystemSpecification
    :param spin_lock_time: Quantity containing spin locking time
    :param spin_lock_frequency: Quantity containing spin locking frequency
    :param adc_samples: int containing the number of ADC samples
                        during the prepulse. If adc_samples=0,
                        no adc is integrated. Useful for debugging and
                        monitoring the signal during spin lock pulse.
    """
    pulse90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                           flip_angle=Quantity(90, 'degrees'),
                                           duration=Quantity(5., 'us'),
                                           frequency_offset=Quantity(0, 'Hz'),
                                           phase_offset=Quantity(0, 'rad'),
                                           delay=Quantity(0, "ms"),
                                           name="+90x")

    pulse180y = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=Quantity(180, 'degrees'),
                                             duration=Quantity(5., 'us'),
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration + spin_lock_time / 4,
                                             name="+180y")

    pulseneg180y = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                                flip_angle=Quantity(180, 'degrees'),
                                                duration=Quantity(5., 'us'),
                                                frequency_offset=Quantity(0, 'Hz'),
                                                phase_offset=Quantity(-np.pi / 2, 'rad'),
                                                delay=(pulse90.duration + 3 * spin_lock_time / 4
                                                       + pulse180y.duration),
                                                name="-180y")

    pulseneg90 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                              flip_angle=Quantity(-90, 'degrees'),
                                              duration=Quantity(5., 'us'),
                                              frequency_offset=Quantity(0, 'Hz'),
                                              phase_offset=Quantity(0, 'rad'),
                                              delay=(spin_lock_time + pulse90.duration +
                                                     pulse180y.duration + pulseneg180y.duration),
                                              name="-90x")

    # calculate the "flip angle" from the SL frequency and SL time
    sl_flipangle = (spin_lock_frequency * spin_lock_time).to("degree")

    slpulse_1 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=pulse90.duration,
                                             name="SL+y")

    slpulse_2 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(-np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time / 4
                                                    + pulse180y.duration),
                                             name="SL-y")

    slpulse_3 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time / 2
                                                    + pulse180y.duration),
                                             name="SL+y")

    slpulse_4 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs,
                                             flip_angle=sl_flipangle / 4,
                                             duration=spin_lock_time / 4,
                                             frequency_offset=Quantity(0, 'Hz'),
                                             phase_offset=Quantity(-np.pi / 2, 'rad'),
                                             delay=(pulse90.duration + spin_lock_time * (3 / 4)
                                                    + pulse180y.duration + pulseneg180y.duration),
                                             name="SL-y")

    if adc_samples > 0:
        adc_duration = (pulse90.duration + spin_lock_time + pulse180y.duration +
                        pulseneg180y.duration + pulseneg90.duration)
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(system_specs=system_specs,
                                                                num_samples=adc_samples,
                                                                duration=adc_duration)
        return cmrseq.Sequence(
            [adc, pulse90, slpulse_1, pulse180y, slpulse_2, slpulse_3, pulseneg180y,
             slpulse_4, pulseneg90], system_specs=system_specs)
    else:
        return cmrseq.Sequence([pulse90, slpulse_1, pulse180y, slpulse_2, slpulse_3, pulseneg180y,
                                slpulse_4, pulseneg90], system_specs=system_specs)
