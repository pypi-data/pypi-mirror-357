""" This module contains parametric definitions for cartesian readouts, 
as well as helper functions associated with cartesian sequence design."""
__all__ = ["multi_line_cartesian", "gre_cartesian_line", "balanced_gre_cartesian_line",
           "se_cartesian_line", "matrix_to_kspace_2d", "get_shortest_adc_duration",
           "get_longest_adc_duration"]

import warnings
from copy import deepcopy
from pint import Quantity
import numpy as np

import cmrseq
from cmrseq._exceptions import AutomaticOptimizationWarning


# pylint: disable=W1401, R0914
def multi_line_cartesian(system_specs: cmrseq.SystemSpec,
                         fnc: callable,
                         matrix_size: np.ndarray,
                         inplane_resolution: Quantity,
                         dummy_shots: int = None, **kwargs):
    """ Creates a list of sequences, one for each k-space_line for a given single-line-definiton
    e.g. se_cartesian_line, gre_cartesian_line

    **Example:**
    .. code-block: python

        ro_blocks = cmrseq.seqdefs.readout.multi_line_cartesian(
                                    system_specs=system_specs,
                                    fnc=cmrseq.seqdefs.readout.gre_cartesian_line,
                                    matrix_size=matrix_size,
                                    inplane_resolution=inplane_resolution,
                                    adc_duration=adc_duration,
                                    prephaser_duration=ss_refocus.duration,
                                    dummy_shots=dummy_shots)

    :param system_specs: SystemSpecification
    :param fnc: callable
    :param matrix_size: array of shape (2, )
    :param inplane_resolution: Quantity[Length] of shape (2, )
    :param dummy_shots: number of shots without adc-events
    :param kwargs: is forwared to call fnc. may not contain
                        num_samples, k_readout, k_phase, prephaser_duration
    :return:
    """
    # kro_max = 1 / inplane_resolution[0]
    # fov_pe = matrix_size[1] * inplane_resolution[1]
    # delta_kpe = 1 / fov_pe
    # if matrix_size[1] % 2 == 1:
    #     kpes = (np.arange(0, matrix_size[1], 1) - (matrix_size[1]) // 2) * delta_kpe
    # else:
    #     kpes = (np.arange(0, matrix_size[1], 1) - (matrix_size[1] + 1) // 2) * delta_kpe

    _, kpes, kro_max = matrix_to_kspace_2d(matrix_size, inplane_resolution)

    # Figure out prephaser shortest prephaser duration for maximal k-space traverse
    prephaser_duration = kwargs.get("prephaser_duration", None)
    if prephaser_duration is None:
        seq_max = fnc(system_specs, num_samples=matrix_size[0], k_phase=kpes[0], k_readout=kro_max,
                      **kwargs)
        prephaser_block = seq_max.get_block("ro_prephaser_0")
        prephaser_duration = system_specs.time_to_raster(prephaser_block.duration, "grad")
        kwargs["prephaser_duration"] = prephaser_duration

    sequence_list = []
    # Add dummy shots
    if dummy_shots is not None:
        # Temporary fix for bSSFP dummy mismatch
        dummy = fnc(system_specs, num_samples=matrix_size[0], k_readout=kro_max, k_phase=0 * kro_max, **kwargs)
        dummy.remove_block('adc_0')
        for _ in range(dummy_shots):
            sequence_list.append(deepcopy(dummy))

    for idx, kpe in enumerate(kpes):
        seq = fnc(system_specs, num_samples=matrix_size[0], k_readout=kro_max,
                  k_phase=kpe, **kwargs)
        sequence_list.append(seq)
    return sequence_list


def matrix_to_kspace_2d(matrix_size: np.ndarray, inplane_resolution: Quantity) -> (np.ndarray, np.ndarray):
    """Calculates maximal k-space vector and phase encoding for each line for a bottom up filling.

    The k-space center will allway be covered by a line, therefore:

        - For an even number of k-space lines the first line at -kmax_pe  and
          the last line is at +kmax_pe - delta_kpe
        - For and odd number the lines are symmetric around the center in pe direction

    :param matrix_size: (2, ) Integer array providing the inplane matrix size
    :param inplane_resolution: (2, ) Quantity with length-dimension providing
                                 the inplane resolution
    :return: k_max (2, ), k-phase positions in phase encoding direction
    """
    kro_traverse = 1 / inplane_resolution[0]
    fov_pe = matrix_size[1] * inplane_resolution[1]
    delta_kpe = 1 / fov_pe
    if matrix_size[1] % 2 == 1:
        kpes = (np.arange(0, matrix_size[1], 1) - (matrix_size[1]) // 2) * delta_kpe
    else:
        kpes = (np.arange(0, matrix_size[1], 1) - (matrix_size[1] + 1) // 2) * delta_kpe

    delta_kro = 1 / (matrix_size[0] * inplane_resolution[0])
    kro_max = - ((matrix_size[1] + 1) // 2) * delta_kpe
    kpe_max = - ((matrix_size[1] + 1) // 2) * delta_kpe
    kmax = Quantity([kro_max.m_as("1/m"), kpe_max.m_as("1/m")], "1/m")
    return kmax, kpes, kro_traverse

def get_shortest_adc_duration(system_specs: cmrseq.SystemSpec,
                              num_samples: int, resolution: Quantity) \
                              -> (Quantity, Quantity, Quantity):
    """Computes the shortest possible single-line readout gradient (without prephaser)
    for the given resolution and matrix size in RO direction.

    Assumes gradients are ramped with maximum slew-rate.

    :param system_specs:
    :param num_samples:
    :param resolution:
    :return: gradient object for the readout gradient and adc object 
    """
    _, _, kro_traverse = cmrseq.seqdefs.readout.matrix_to_kspace_2d(np.array([num_samples, 1]),
                                                         Quantity([resolution.m_as("mm"), 1], "mm"))
    
    dk_M = kro_traverse/num_samples # Get kspace step
    farea_ro = (kro_traverse / system_specs.gamma).to("mT/m*ms")

    # The naive approach would be to assume maximum gradient strength, however this is not actually the shortest due to rise time
    # We already know the flat area of the gradient, so we need to minimize the rise area. 
    # This also minimizes the prewinder, resulting in the fastest possible sequence

    # The duration is given by D = A/G + 2G/s, find G to minimize D (A=area of flat area, s=max slew, G=gradient strength)
    # Which has a minima at G = sqrt(A*S/2)

    g_opt = np.sqrt(farea_ro*system_specs.max_slew/2)

    if g_opt>system_specs.max_grad:
        g_opt = system_specs.max_grad

    # Solve for dwell time at optimal gradient strength
    min_dwell = (dk_M/system_specs.gamma/g_opt).to('ms')
    # round up to nearest adc_raster multiple
    dwell = system_specs.time_to_raster(min_dwell,raster='adc')
    
    adc_duration = dwell*num_samples

    # Generate ADC
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
    ro_amp = (dk_M / adc_dwell / system_specs.gamma).to("mT/m")

    ro = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(system_specs=system_specs,
                                                orientation = np.array([1.,0.,0.]),
                                                amplitude = ro_amp, flat_duration = ro_flatdur)

    return ro, adc


def get_longest_adc_duration(system_specs: cmrseq.SystemSpec,
                             total_duration: Quantity,
                             num_samples: int,
                             resolution: Quantity,
                             balanced: bool = False,
                             additional_kspace_traverse: Quantity = None,
                             max_iters:int = 3) \
                             -> (cmrseq.bausteine.TrapezoidalGradient, cmrseq.bausteine.TrapezoidalGradient):
    """Creates the readout-gradient and prephaser (and balancing rewinder) with maximum flat top
    duration of the readout gradient, for the specified flat top area (defined by the
    image resoultion) and a specified total duration.

    :param system_specs:
    :param total_duration: Total duration to fit the gradients into.
    :param num_samples: Number of samples (used to compute the required k-space traverse)
    :param resolution: Resolution in RO direction (used to compute the required k-space traverse)
    :param balanced: If true, the total duration includes the rewinder after the readout, otherwise not
    :param additional_kspace_traverse: k-space vector that needs to be traversed during the prephaser,
                                       while adhering to the norm of the combined gradient channels
                                       being smaller than system_specs.max_grad. If None, no additional
                                       traverse is assumed, potentially resulting in higher prephaser
                                       amplitudes.
    :param max_iters: optional, maximum number of iteration loops for finding optimal gradients. Typically converges with less than 4
    :return: Two trapezoidal gradient objects, one for the prephaser and the other for the readout gradient, and one ADC object
    """

    kmax, _, kro_traverse = cmrseq.seqdefs.readout.matrix_to_kspace_2d(np.array([num_samples, 1]),
                                                         Quantity([resolution.m_as("mm"), 1], "mm"))
    area_ro = (kro_traverse / system_specs.gamma).m_as("mT/m*ms")

    # Only questions that needs to be solved is what is G_readout
    # since the area of the readout is set, then knowing G_readout gives us the flat time of the readout and its ramp times, basically the entire gradient

    # An initial guess for G_readout can be made by ignoring ramp times for the readout

    farea_ro = (kro_traverse / system_specs.gamma).to("mT/m*ms")

    # Get estimated area of prephaser as half readout + traverse
    # This ignores ramping for the readout, so the actual one will be larger...
    if additional_kspace_traverse is not None:
        k_y_area = np.abs((additional_kspace_traverse[0] / system_specs.gamma).to("mT/m*ms"))
        k_z_area = np.abs((additional_kspace_traverse[1] / system_specs.gamma).to("mT/m*ms"))
        area_prep_est = np.sqrt((farea_ro/2)**2 + k_y_area**2 + k_z_area**2)
    else:
        area_prep_est = farea_ro/2
        k_y_area = Quantity(0,'mT/m*ms')
        k_z_area = Quantity(0,'mT/m*ms')

    # Get the shortest possible duration for this prep
    _, fastest_prep_ramp, fastest_prep_flatdur = system_specs.get_shortest_gradient(area_prep_est)

    # From this we can get the available time for readout
    prep_duration_est = fastest_prep_flatdur + 2*fastest_prep_ramp
    if balanced:
        readout_duration_est = total_duration - 2*prep_duration_est
    else:
        readout_duration_est = total_duration - prep_duration_est
    # Solve for inital guess of readout gradient amplitude from given farea and duration
    a = 2/system_specs.max_slew
    b = -readout_duration_est
    c = farea_ro
    if b**2<(4*a*c):
        raise cmrseq.err.SequenceArgumentError(f"Total duration too short for desired kspace traverse",
                                        argument="total_duration")
    
    g = (-b - np.sqrt(b**2-4*a*c))/(2*a)

    # This is our first guess for the readout amplitude, and gives us a lower bound on the possible strength
    # This is because accounting for readout ramps in the prephaser will increase its duration, resulting in less time for readout and higher gradients
    # And then larger ramps, and more prephaser area and so on...
    # If this is larger than max, the sequence is not possible
    if g > system_specs.max_grad or readout_duration_est<0:
        raise cmrseq.err.SequenceArgumentError(f"Total duration too short for desired kspace traverse",
                                               argument="total_duration")

    # now we construct the actual sequence components
    # This uses a few steps of optimization

    for i in range(max_iters):
        # Step 1: 
        # create readout gradient with these specs that abides by rasters
        ro = cmrseq.bausteine.TrapezoidalGradient.from_dur_amp(system_specs=system_specs,
                                                        orientation = np.array([1.,0.,0.]),
                                                        amplitude = g, duration=readout_duration_est)
        # Step 2: 
        # ADC must be on raster, but to achieve the desired kspace step, we need to adjust the readout gradient strength to match adc dwell
        # Create an ADC object
        adc_duration = ro.flat_duration
        adc = cmrseq.bausteine.SymmetricADC.from_centered_valid(
                system_specs=system_specs,
                num_samples=num_samples,
                duration=adc_duration,
                delay=Quantity(0,'ms'), suppress_warnings=True)
        
        adc_dwell = adc._dwell
        # RO flat duration is set such that it includes all ADC samples + half a dwell time on either side, rounded up to gradient raster
        ro_flatdur = np.around(np.max(np.abs(adc.adc_timing-adc.adc_center)),decimals=8)*2+adc._dwell
        ro_flatdur = system_specs.time_to_raster(ro_flatdur, raster="grad")
        
        # RO amplitude is based on deltaK
        dk_M = kro_traverse/num_samples 
        ro_amp = (dk_M / adc_dwell / system_specs.gamma).to("mT/m")

        # If this is larger than max, the sequence is not possible
        if ro_amp > system_specs.max_grad:
            raise cmrseq.err.SequenceArgumentError(f"Total duration too short for desired kspace traverse",
                                                    argument="total_duration")
        # Create updated readout gradient
        ro = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(system_specs=system_specs,
                                                        orientation = np.array([1.,0.,0.]),
                                                        amplitude = ro_amp, flat_duration = ro_flatdur)
        
        # Create corresponding prephaser
        A_prep = np.sqrt((ro.area[0]/2)**2 + k_y_area**2 + k_z_area**2)
        prep = cmrseq.bausteine.TrapezoidalGradient.from_area(system_specs=system_specs,
                                                        orientation = np.array([1.,0.,0.]),area=A_prep)
        
        # Calculate final duration
        if balanced:
            final_duration = ro.duration + 2*prep.duration
        else:
            final_duration = ro.duration + prep.duration

        if final_duration > total_duration:
            # Adjust estimated readout duration
            readout_duration_est -= (final_duration-total_duration)
        else:
            break

    # Create final version of prep on proper axes
    prep_dir = np.array([(ro.area[0]/2).m_as('mT/m*ms'),k_y_area.m_as('mT/m*ms'),k_z_area.m_as('mT/m*ms')])
    prep_dir = prep_dir/np.linalg.norm(prep_dir)
    prep_dir[0] *= -1
    prep = cmrseq.bausteine.TrapezoidalGradient.from_area(system_specs=system_specs,
                                                    orientation = prep_dir,area=A_prep)
    return prep, ro, adc


# pylint: disable=W1401, R0913, R0914
def gre_cartesian_line(system_specs: cmrseq.SystemSpec,
                       num_samples: int,
                       k_readout: Quantity,
                       k_phase: Quantity,
                       adc_duration: Quantity,
                       delay: Quantity = Quantity(0., "ms"),
                       prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """Generates a gradient sequence to apply phase encoding (0, 1.,0.) direction and a readout
    including adc-events for a single line in gradient direction (1., 0., 0.). Is designed to work
    for gradient-echo based readouts.

    .. code-block:: python

       . ADC:                      ||||||     -> num_samples    .
       .                           ______                       .
       . RO:      ___________     /      \                      .
       .                     \___/                              .
       .                      ___                               .
       . PE:      ___________/   \________                      .
       .                                                        .
       .         | delay    |     |     |                       .
       .                        adc_duration                    .

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`   s
    :param k_phase: Quantity[1/Length] :math:`n \Delta k_{y}` phase encoding strength of
                        current line
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param delay:
    :param prephaser_duration: Optional - if not specified the shortest possible duration for the
                                RO/PE prephaser is calculated
    :return: Sequence object containing RO- & PE-gradients as well as ADC events
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
        dk_M = k_readout/num_samples 
        ro_amp = (dk_M / adc_dwell / system_specs.gamma).to("mT/m")
    else:
        # Calculate based on only adc_duration and k_readout
        adc_duration = system_specs.time_to_raster(adc_duration, raster="grad")
        ro_amp = (k_readout / adc_duration / system_specs.gamma).to("mT/m")
        ro_flatdur = adc_duration

    readout_pulse = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        flat_duration=ro_flatdur,
        amplitude=ro_amp, delay=Quantity(0., "ms"),
        name="trapezoidal_readout"
    )

    prephaser_ro_area = readout_pulse.area[0] / 2.
    prephaser_pe_area = np.abs(k_phase / system_specs.gamma)

    # Total gradient traverse is a combination of ro and pe directions.
    # Need to solve as single gradient to ensure slew and strength restrictions are met
    k_traverse_comb = Quantity([(prephaser_ro_area * system_specs.gamma).m_as("1/m"),
                                 k_phase.m_as("1/m"), 0.], "1/m")
    _, fastest_prep_ramp, fastest_prep_flatdur = system_specs.get_fastest_kspace_traverse(k_traverse_comb)

    # If prephaser duration was not specified use the fastest possible prephaser
    min_duration = fastest_prep_flatdur + 2 * fastest_prep_ramp
    if prephaser_duration is None:
        prephaser_duration = min_duration
    else:
        # Check if duration is sufficient for _combined_ prephaser gradients
        if prephaser_duration.m_as("ms") < min_duration.m_as("ms") - 1e-6:
            raise cmrseq.err.SequenceArgumentError(
                    f"Too short for combined PE+RO k-space traverse."
                    f" ({prephaser_duration} < {min_duration})",
                    argument="prephaser_duration")
    readout_pulse.shift(prephaser_duration + delay)

    total_kspace_traverse = Quantity(np.linalg.norm(k_traverse_comb.m_as("1/m")), "1/m")
    combined_gradient_area = total_kspace_traverse / system_specs.gamma.to("1/mT/ms")
    orientation = (k_traverse_comb/np.sqrt(np.sum(k_traverse_comb**2))).m_as('')
    prep_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs=system_specs,
                                                                    orientation=orientation,
                                                                    duration=prephaser_duration,
                                                                    area=combined_gradient_area,
                                                                    delay=delay, name="ro_prephaser")
    

    ro_prep_pulse = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                        orientation=np.array([-1., 0., 0.]),
                                                        amplitude=prep_pulse.gradients[1][0,1],
                                                        flat_duration=prep_pulse.flat_duration,
                                                        rise_time=prep_pulse.rise_time,
                                                        delay=delay, name="ro_prephaser")

    pe_direction = np.array([0., 1., 0.])# * np.sign(k_phase)
    pe_prep_pulse = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                    orientation=pe_direction,
                                                    amplitude=prep_pulse.gradients[1][1,1],
                                                    flat_duration=prep_pulse.flat_duration,
                                                    rise_time=prep_pulse.rise_time,
                                                    delay=delay, name="pe_prephaser")

    if num_samples > 0:
        adc_delay = prephaser_duration + delay - adc.adc_center + readout_pulse.duration/2
        # ADC delay must be on ADC raster, otherwise sample edges will not be on raster
        adc_delay = system_specs.time_to_raster(adc_delay, raster="adc")
        adc.shift(adc_delay)
        return cmrseq.Sequence([ro_prep_pulse, pe_prep_pulse, readout_pulse, adc],
                               system_specs=system_specs)
    else:
        return cmrseq.Sequence([ro_prep_pulse, pe_prep_pulse, readout_pulse],
                               system_specs=system_specs)


# pylint: disable=W1401, R0913, R0914
def balanced_gre_cartesian_line(system_specs: cmrseq.SystemSpec,
                                num_samples: int,
                                k_readout: Quantity,
                                k_phase: Quantity,
                                adc_duration: Quantity,
                                delay: Quantity = Quantity(0., "ms"),
                                prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """ Generates a gradient sequence to apply phase encoding (0, 1.,0.) direction and a readout
    including adc-events for a single line in gradient direction (1., 0., 0.). After readout
    prephasers are rewound. Is designed to work for gradient-echo based readouts.

    .. code-block: python

       .        ADC:                      ||||||     -> num_samples        .
       .                                  ______                           .
       .        RO:      ___________     /      \     ______               .
       .                            \___/        \___/                     .
       .                             ___          ___                      .
       .        PE:      ___________/   \________/   \_____                .
       .                                                                   .
       .                | delay    |     |     |                           .
       .                              adc_duration                         .

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`   s
    :param k_phase: Quantity[1/Length] :math:`n \Delta k_{y}` phase encoding
                        strength of current line
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param delay: Defaults to 0 ms
    :param prephaser_duration: Optional - if not specified the shortest possible duration for the
                                RO/PE prephaser is calculates
    :return: Sequence object containing RO- & PE-gradients plus rewinders as well as ADC events
    """
    seq = gre_cartesian_line(system_specs=system_specs, num_samples=num_samples,
                             k_readout=k_readout, k_phase=k_phase,
                             adc_duration=adc_duration, delay=delay,
                             prephaser_duration=prephaser_duration)
    # Copy prephasers
    prep_ro_block = deepcopy(seq.get_block("ro_prephaser_0"))
    prep_pe_block = deepcopy(seq.get_block("pe_prephaser_0"))

    # Shift to end of readout
    ro_duration = seq["trapezoidal_readout_0"].duration
    prep_pe_block.shift(ro_duration + prep_pe_block.duration)
    prep_ro_block.shift(ro_duration + prep_ro_block.duration)

    # Invert amplidute
    prep_pe_block.scale_gradients(-1)

    prep_pe_block.name = "pe_prephaser_balance"
    prep_ro_block.name = "ro_prephaser_balance"

    seq += cmrseq.Sequence([prep_ro_block, prep_pe_block], system_specs=system_specs)
    return seq


# pylint: disable=W1401, R0913, R0914
def se_cartesian_line(system_specs: cmrseq.SystemSpec,
                      num_samples: int,
                      echo_time: Quantity,
                      pulse_duration: Quantity,
                      excitation_center_time: Quantity,
                      k_readout: Quantity,
                      k_phase: Quantity,
                      adc_duration: Quantity,
                      delay: Quantity = Quantity(0., "ms"),
                      prephaser_duration: Quantity = None) -> cmrseq.Sequence:
    """ Generates a gradient sequence to apply phase encoding (0, 1.,0.) direction and a readout
    including adc-events for a single line in gradient direction (1., 0., 0.) for a spin-echo based
    readout.

    .. code-block:: python

        .                excitation center                                  .
        .                   |                                               .
        .                   |   TE/2 |   TE/2 |                             .
        .   ADC:                           ||||||     -> num_samples        .
        .                      ___         ______                           .
        .   RO:           ____/   \_______/      \                          .
        .                      ___                                          .
        .   PE:           ____/   \_____________                            .
        .           |   |                 |     |                           .
        .           delay              adc_duration                         .
        .               |    |                                              .
        .           pulse_duration                                          .


    :raises ValueError: If phase/frequency encoding amplitude would exceed system limits

    :param system_specs: SystemSpecification
    :param num_samples: Number of samples acquired during frequency encoding
    :param echo_time:
    :param pulse_duration: total time of ss-gradient (including ramps)
    :param excitation_center_time: Quantity[Time] Reference time-point to calculate TE from
    :param k_readout: Quantity[1/Length] :math:`FOV_{kx}` corresponds to :math:`1/\Delta x`
    :param k_phase: Quantity[1/Length] :math:`n \Delta k_{y}` phase encoding
                            strength of current line
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param prephaser_duration: Optional - if not specified the shortest possible duration for the
                                RO/PE prephaser is calculates
    :return: Sequence containing the RO/PE prephaser, RO and adc events for a spin-echo read-out
    """

    # First calculate ADC, and determine the actual dwell time
    # Get raster-rounded ADC
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
    dk_M = k_readout/num_samples 
    ro_amp = (dk_M / adc_dwell / system_specs.gamma).to("mT/m")

    # Check if viable ADC for SE
    rise_time = system_specs.get_shortest_rise_time(ro_amp)
    if ro_flatdur >= (echo_time / 2 - rise_time - pulse_duration / 2) * 2:
        raise ValueError("Specified ADC-duration is larger than available time from "
                         "end of refocusing pulse to Echo center")

    ro_delay = delay + excitation_center_time + echo_time - ro_flatdur / 2
    readout_pulse = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        flat_duration=ro_flatdur,
        amplitude=ro_amp, delay=ro_delay,
        name="readout_grad")
    readout_pulse.shift(-readout_pulse.rise_time)
    prephaser_ro_area = readout_pulse.area[0] / 2.
    prephaser_pe_area = np.abs(k_phase / system_specs.gamma)

    # Total gradient traverse is a combination of ro and pe directions.
    # Need to solve as single gradient to ensure slew and strength restrictions are met
    combined_kspace_traverse = np.sqrt((prephaser_ro_area * system_specs.gamma) ** 2 + k_phase ** 2)
    [_, fastest_prep_ramp, fastest_prep_flatdur] = system_specs.get_shortest_gradient(
        combined_kspace_traverse / system_specs.gamma)

    # If prephaser duration was not specified use the fastest possible prephaser
    if prephaser_duration is None:
        prephaser_duration = fastest_prep_flatdur + 2 * fastest_prep_ramp
    else:
        if prephaser_duration < fastest_prep_flatdur + 2 * fastest_prep_ramp:
            raise ValueError("Prephaser duration is to short to for combined PE+RO "
                             "k-space traverse.")

    prephaser_delay = delay + echo_time / 2 - pulse_duration / 2 \
                      - prephaser_duration + excitation_center_time
    ro_prep_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(
        system_specs=system_specs,
        orientation=np.array([1., 0., 0.]),
        duration=prephaser_duration,
        area=prephaser_ro_area,
        delay=prephaser_delay,
        name="ro_prephaser")

    pe_direction = np.array([0., -1., 0.]) * np.sign(k_phase)
    pe_prep_pulse = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs=system_specs,
                                                                       orientation=pe_direction,
                                                                       duration=prephaser_duration,
                                                                       area=prephaser_pe_area,
                                                                       delay=prephaser_delay,
                                                                       name="pe_prephaser")
    adc_delay = readout_pulse.tmin + readout_pulse.rise_time + readout_pulse.flat_duration/2 - adc.adc_center
    adc.shift(adc_delay)
    return cmrseq.Sequence([ro_prep_pulse, pe_prep_pulse, readout_pulse, adc],
                           system_specs=system_specs)
