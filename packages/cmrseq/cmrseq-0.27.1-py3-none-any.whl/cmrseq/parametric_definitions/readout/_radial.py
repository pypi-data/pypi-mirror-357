""" This module contains parametric definitions for generating radial readouts, as well as 3D radial ordering schemes."""
__all__ = ["radial_spoke","radial_3D","radial_3D_spiral_phyllotaxis","radial_3D_spiral_WongRoos"]

from copy import deepcopy
from pint import Quantity
import numpy as np

import cmrseq

def radial_spoke(system_specs: cmrseq.SystemSpec,
                 num_samples: int,
                 kr_max: Quantity,
                 angle: Quantity,
                 adc_duration: Quantity,
                 delay: Quantity = Quantity(0., "ms"),
                 prephaser_duration: Quantity = None,
                 balanced:bool = False) -> cmrseq.Sequence:
    
    """Generates a single 2D radial spoke that traverses from [-kr_max,kr_max] at a given angle.

    :param system_specs:
    :param num_samples: Number of samples from [-kr_max,kr_max].
    :param kr_max: Quantity[1/length] maximum radius of kspace traverse
    :param angle: Quantity[angle] Angle of spoke in M-P plane. Angle of 0 corresponds to readout direction
    :param adc_duration: Quantity[time] Total duration of adc-sampling in ms
    :param delay: 
    :param prephaser_duration: Quantity[time] Optional - if not specified the shortest possible
                               duration for the prephaser is calculated
    :param balanced: Optional - Setting to True adds rewinder gradient after ADC to ensure 0th moment balance
    :return: Sequence containing radial readout
    """

        # First calculate ADC, and determine the actual dwell time
    if num_samples > 0:
        # Get raster-rounnded ADC
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(
                system_specs=system_specs,
                num_samples=num_samples,
                duration=adc_duration,
                delay=Quantity(0,'ms'))
        adc_dwell = adc._dwell
        # RO flat duration is set such that it includes all ADC samples + half a dwell time on either side, rounded up to gradient raster
        ro_flatdur = np.around(np.max(np.abs(adc.adc_timing-adc.adc_center)),decimals=8)*2+adc._dwell
        ro_flatdur = system_specs.time_to_raster(ro_flatdur, raster="grad")

        # RO amplitude is based on deltaK
        dk_M = 2.*kr_max/num_samples 
        ro_amp = (dk_M / adc_dwell / system_specs.gamma).to("mT/m")
    else:
        # Calculate based on only adc_duration and k_readout
        adc_duration = system_specs.time_to_raster(adc_duration, raster="grad")
        ro_amp = (2 * kr_max / adc_duration / system_specs.gamma).to("mT/m")
        ro_flatdur = adc_duration

    readout_pulse = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        flat_duration=ro_flatdur,
        amplitude=ro_amp, delay=Quantity(0., "ms"),
        name="radial_readout"
    )

    prephaser_area = readout_pulse.area[0] / 2.
    [_, fastest_prep_ramp, fastest_prep_flatdur] = system_specs.get_shortest_gradient(prephaser_area)

    if prephaser_duration is None:
        prephaser_duration = fastest_prep_flatdur + 2 * fastest_prep_ramp
    else:
        # Check if duration is sufficient for _combined_ prephaser gradients
        if prephaser_duration < np.round(fastest_prep_flatdur + 2 * fastest_prep_ramp, 7):
            raise ValueError("Prephaser duration is to short for combined PE+RO k-space traverse.")

    readout_pulse.shift(prephaser_duration + delay)

    prephaser_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
        system_specs=system_specs,
        orientation=np.array([-1., 0., 0.]),
        duration=prephaser_duration,
        area=prephaser_area,
        delay=delay, name="radial_prephaser")

    if num_samples > 0:
        adc_delay = prephaser_duration + delay - adc.adc_center + readout_pulse.duration/2
        adc.shift(adc_delay)
        seq = cmrseq.Sequence([prephaser_pulse, readout_pulse, adc],
                               system_specs=system_specs)
    else:
        seq = cmrseq.Sequence([prephaser_pulse, readout_pulse],
                               system_specs=system_specs)

    if balanced:  
        # Copy prephasers
        rewind_block = deepcopy(seq.get_block("radial_prephaser_0"))

        # Shift to end of readout
        ro_duration = seq.get_block("radial_readout_0").duration
        rewind_block.shift(ro_duration + rewind_block.duration)

        rewind_block.name = "radial_prephaser_balance"

        seq += cmrseq.Sequence([rewind_block], system_specs=system_specs)

    sa = np.sin(angle).m_as('dimensionless')
    ca = np.cos(angle).m_as('dimensionless')

    omatrix = cmrseq.OMatrix(system_specs=system_specs,
                             position=Quantity(0,'m'),
                             slice_normal=np.array([0,0,1]),
                             readout_direction = np.array([ca,sa,0]))

    seq.register_omatrix(matrix=omatrix, gradients=seq.blocks)

    return seq

def radial_3D(system_specs: cmrseq.SystemSpec,
              spoke_directions: np.array,
              samples_per_spoke: int,
              kr_max: Quantity,
              adc_duration: Quantity,
              prephaser_duration: Quantity = None,
              balanced:bool = False):
    
    """Generates list of sequences rotated such that readout directions correspond to 'spoke_directions'

    :param system_specs:
    :param spoke_directions: (N,3), Spoke directions in [X,Y,Z] for N spokes
    :param samples_per_spoke: Number of samples from [-kr_max,kr_max]
    :param kr_max: Quantity[1/length] maximum radius of kspace traverse
    :param adc_duration: Quantity[time] Total duration of adc-sampling in ms
    :param prephaser_duration: Quantity[time] Optional - if not specified the shortest possible
                               duration for the prephaser is calculated
    :param balanced: Optional - Setting to True adds rewinder gradient after ADC to ensure 0th moment balance
    :return: List of sequences
    """
    
    ref_spoke = radial_spoke(system_specs=system_specs,
                            angle=Quantity(0., 'rad'),
                            num_samples=samples_per_spoke,
                            kr_max=kr_max,
                            adc_duration=adc_duration,
                            prephaser_duration=prephaser_duration,
                            balanced=balanced)
    
    seq_list = []
    
    for readout_direction in spoke_directions:
        if readout_direction[0]!=0 and readout_direction[1]!=0:
            slice_direction = np.array([readout_direction[1],-readout_direction[0], 0]) # X,Y,Z
        else:
            slice_direction = np.array([1,0,0])

        omatrix = cmrseq.OMatrix(system_specs=system_specs,
                                 position=Quantity(0,'m'),
                                 slice_normal=slice_direction,
                                 readout_direction = readout_direction)
    
        seq = deepcopy(ref_spoke)
        seq.register_omatrix(omatrix,gradients=ref_spoke.blocks)
        seq_list.append(seq)

    return seq_list


def radial_3D_spiral_WongRoos(num_interleaves: int,
                          spokes_per_interleave: int,
                          single_hemisphere: bool = False):
    """Generates 3D radial spoke ordering according to :
        Wong STS, Roos MS. 
        A strategy for sampling on a sphere applied to 3D selective RF pulse design. 
        Magnetic Resonance in Medicine. 1994;32(6):778-784. doi:10.1002/mrm.1910320614



    :param num_interleaves: number of spiral interleaves
    :param spokes_per_interleave: number of radial spokes per interleave
    :param single_hemisphere: flag to restrict spiral to single half of sphere
    :return: array (N,3), Spoke directions in [X,Y,Z] for N spokes
    """

    spoke_directions = []

    if not single_hemisphere:
        spoke_directions.append([0,0,1])
    for interleave in range(num_interleaves):
        for spoke in range(spokes_per_interleave):

            if single_hemisphere:
                z = 1 - (spoke + 1) / spokes_per_interleave
            else:
                z = -(2 * (spoke + 1) - spokes_per_interleave - 1) / spokes_per_interleave * (-1) ** interleave

            x = np.cos(np.sqrt(spokes_per_interleave / num_interleaves * np.pi) * np.arcsin(
                z) + 2 * interleave * np.pi / num_interleaves) * np.sqrt(1 - z ** 2)
            y = np.sin(np.sqrt(spokes_per_interleave / num_interleaves * np.pi) * np.arcsin(
                z) + 2 * interleave * np.pi / num_interleaves) * np.sqrt(1 - z ** 2)
            
            spoke_directions.append([x,y,z])

    return np.array(spoke_directions)


def radial_3D_spiral_phyllotaxis(num_interleaves: int,
                                 spokes_per_interleave: int,
                                 single_hemisphere: bool = False):
    """Generates 3D radial spoke ordering according to :
        Piccini D, Littmann A, Nielles-Vallespin S, Zenge MO. Spiral phyllotaxis: 
        The natural way to construct a 3D radial trajectory in MRI. 
        Magnetic Resonance in Medicine. 2011;66(4):1049-1056. doi:10.1002/mrm.22898

    :param num_interleaves: number of spiral interleaves
    :param spokes_per_interleave: number of radial spokes per interleave
    :param single_hemisphere: flag to restrict spiral to single half of sphere
    :return: array (N,3), Spoke directions in [X,Y,Z] for N spokes
    """

    N_total = num_interleaves * spokes_per_interleave
    GA = 137.51 / 180 * np.pi

    if single_hemisphere:  # As per publication
        angles_az = (np.arange(0, N_total) * GA).reshape(spokes_per_interleave, num_interleaves).T
        angles_polar = (np.pi / 2 * np.sqrt(np.arange(0, N_total) / N_total)).reshape(spokes_per_interleave,
                                                                                      num_interleaves).T
    else:  # Modified to continue traverse into second hemisphere
        N_hem1 = np.ceil(N_total / 2)
        N_hem2 = np.floor(N_total / 2)

        # Angles increase with sqrt(n) until equator, then reverse same scaling in second hemisphere
        angles_polar_1 = np.pi / 2 * np.sqrt(np.arange(0, N_hem1) / N_hem1)
        angles_polar_2 = np.pi / 2 * (2 - np.sqrt((N_hem2 - np.arange(0, N_hem2)) / N_hem1))

        # Azimuthal angles follow GA
        angles_az = (np.arange(0, N_total) * GA).reshape(spokes_per_interleave, num_interleaves).T

        # Combine set of angles and reshape into array
        angles_polar = np.concatenate([angles_polar_1, angles_polar_2])
        angles_polar = angles_polar.reshape(spokes_per_interleave, num_interleaves).T

        # Reverse every second spiral
        angles_polar[1::2, :] = np.flip(angles_polar[1::2, :], axis=1)
        angles_az[1::2, :] = np.flip(angles_az[1::2, :], axis=1)

    spoke_directions = []

    for az_interleave, polar_interleave in zip(angles_az, angles_polar):
        interleave = []
        for az, polar in zip(az_interleave, polar_interleave):
            ca = np.cos(az)
            sa = np.sin(az)

            cp = np.cos(polar)
            sp = np.sin(polar)

            spoke_directions.append(np.array([sp * ca, sp * sa, cp]))

    return np.array(spoke_directions)
