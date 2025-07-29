""" This module contains functions defining compositions of building blocks commonly used
for excitation in MRI """
__all__ = ["sms_pulse",
           "slice_selective_sinc_pulse", "optimize_slice_selection",
           "slice_selective_se_pulses", "spectral_spatial_excitation"]

import math
from copy import deepcopy

import numpy as np
from pint import Quantity

import cmrseq


def sms_pulse(system_specs: cmrseq.SystemSpec,
              single_pulse: cmrseq.bausteine.RFPulse,
              n_slices: int,
              band_gap: Quantity,
              slice_thickness: Quantity,
              modulation_type: str = "quadrature") \
        -> cmrseq.bausteine.RFPulse:
    """Modulates the waveform of a given slice selective excitation pulse using
    the sigpy.mri.rf.dzrf_mb implementation.

    :param system_specs:
    :param single_pulse: Instance of a cmrseq RFPulse or subclass
    :param n_slices: Number of slices to simultaneously excite
    :param band_gap: Distance between the excited slices
    :param slice_thickness: Thickness of the exited slices
    :param modulation_type: from [amplitude, phase, quadrature]
    :return: New pulse object with multi-banded waveform
    """

    import sigpy.mri.rf as sigpy_rf

    modulation_type_lu = {"amplitude": "amp_mod",
                          "phase": "phs_mod",
                          "quadrature": "quad_mod"}
    if modulation_type.lower() not in modulation_type_lu.keys():
        raise cmrseq.err.SequenceArgumentError(
            f"Specified value not in [{list(modulation_type_lu.keys()) + ['None', ]}]",
            argument='modulation_type')

    # convert magnitude from tesla to gauss
    time, rf_waveform = single_pulse._rf
    pulse = rf_waveform.m_as("T") * 10_000 / 2 / np.pi
    tb_product = single_pulse.bandwidth.m_as("kHz") * single_pulse.duration.m_as("ms")
    gap_factor = band_gap.m_as("m") / slice_thickness.m_as("m") * tb_product

    # Call sigpy multibanding
    mb_pulse = sigpy_rf.multiband.mb_rf(pulse.real, n_slices, gap_factor,
                                        modulation_type_lu.get(modulation_type, None))
    # Construct with RF pulse object
    mb_pulse = Quantity(mb_pulse / 10_000 * 2 * np.pi, "T").to("uT")
    pulse_block = cmrseq.bausteine.RFPulse(system_specs, f"sms_{single_pulse.name}",
                                        time=time, rf_waveform=mb_pulse,
                                        frequency_offset=single_pulse.frequency_offset,
                                        phase_offset=single_pulse.phase_offset,
                                        bandwidth=single_pulse.bandwidth,
                                        rf_events=single_pulse.rf_events)
    return pulse_block


# pylint: disable=W1401, R0913, R0914
def slice_selective_sinc_pulse(system_specs: cmrseq.SystemSpec,
                               slice_thickness: Quantity,
                               flip_angle: Quantity,
                               time_bandwidth_product: float = 4,
                               pulse_duration: Quantity = None,
                               delay: Quantity = Quantity(0., "ms"),
                               slice_position_offset: Quantity = Quantity(0., "m"),
                               slice_normal: np.ndarray = np.array([0., 0., 1.]),
                               phase_offset: Quantity = Quantity(0., "rad"),
                               ) -> cmrseq.Sequence:
    """ Defines slice selective excitation using a Sinc-RF pulse and a slice selection gradient.

    .. code-block::

        .                     /\                           .
        .           ______/\ /  \ /\______                 .
        .                  \/   \/                         .
        .                                                  .
        .                __________                        .
        .           ____/          \       ___             .
        .                           \_____/                .
        .               |pulse-dur| |     |                .
        .                       shortest possible          .

    :param system_specs: SystemSpecifications
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param flip_angle: Quantity[Angle] containing the required flip_angle
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :param pulse_duration: Quantity[Time] Optional - Total pulse duration (corresponds to
                           flat_duration of the slice selection gradient). If not specified,
                           the shortest possible pulse-duration within system limits is calculated.
    :param delay: Quantity[Time] added time-offset
    :param slice_position_offset: Quantity[Length] positional offset in slice normal direction
                                  defining the frequency offset of the RF pulse
    :param slice_normal: np.ndarray of shape (3, ) denoting the direction of the slice-normal.
    :return: cmrseq.Sequence
    """
    if pulse_duration is None:
        shortest_pulse = cmrseq.bausteine.SincRFPulse.from_shortest(system_specs=system_specs,
                                                    flip_angle=flip_angle,
                                                    time_bandwidth_product=time_bandwidth_product,
                                                    center=0.5, name="dummy", phase_offset=phase_offset)

        pulse_duration, gradient_amplitude = optimize_slice_selection(system_specs,
                                                     slice_thickness, time_bandwidth_product,
                                                     min_duration=shortest_pulse.duration)
    else:
        rf_bandwidth = time_bandwidth_product / pulse_duration.to("ms")
        gradient_amplitude = (rf_bandwidth / slice_thickness / system_specs.gamma).to("mT/m")

    frequency_offset = (system_specs.gamma.to("1/mT/ms") * slice_position_offset.to("m")
                        * gradient_amplitude.to("mT/m"))

    # Pulse is shifted by delay+rise-time after gradient definition
    rf_block = cmrseq.bausteine.SincRFPulse(system_specs=system_specs, flip_angle=flip_angle,
                                            duration=pulse_duration,
                                            time_bandwidth_product=time_bandwidth_product,
                                            frequency_offset=frequency_offset.to("Hz"),
                                            center=0.5, name="rf_excitation", phase_offset=phase_offset)
    ssgrad = cmrseq.bausteine.TrapezoidalGradient.from_fdur_amp(system_specs=system_specs,
                                                                orientation=slice_normal,
                                                                amplitude=gradient_amplitude,
                                                                flat_duration=pulse_duration,
                                                                name="slice_select")

    rf_block.shift(ssgrad.gradients[0][1])

    ssrefocus = cmrseq.bausteine.TrapezoidalGradient.from_area(
        system_specs=system_specs,
        orientation=-slice_normal,
        area=Quantity(np.abs(np.linalg.norm(ssgrad.area.m_as("mT/m*ms"), axis=-1) / 2), "mT/m*ms"),
        delay=ssgrad.gradients[0][-1],
        name="slice_select_rewind")
    seq = cmrseq.Sequence([rf_block, ssgrad, ssrefocus], system_specs=system_specs)
    if delay is not None:
        seq.shift_in_time(delay)
    return seq

def optimize_slice_selection(system_specs: cmrseq.SystemSpec,
                             slice_thickness: Quantity,
                             time_bandwidth_product: float,
                             min_duration: Quantity = None) \
                             -> (Quantity, Quantity):
    """Computes the shortest possible combination of RF-pulse and trapezoidal
    slice-selection gradient for the given time-bandwidth-product, flip angle and
    slice thickness.

    :param system_specs: SystemSpecifications
    :param slice_thickness: Defines the necessary gradient amplitude
    :param time_bandwidth_product: Used to calculate the RF bandwidth from duration
    :param min_duration: Manually set minimal duration (gradient flat duration) 
                         (e.g. shortest pulse duration according to peak RF power)
    :return: pulse_duration, gradient amplitude
    """
    from scipy.optimize import minimize

    # x = [dur, grad_amp]
    # Minimize the duration of the slice selective excitation (without rewind)
    s = system_specs.max_slew.m_as("mT/m/ms")

    def _optim(x):
        rise_time = x[1] / s
        return (x[0] + 2 * rise_time)

    def _flat_dur(x):
        bandwidth = time_bandwidth_product / (x[0] + 1e-8)
        amp_for_rf = bandwidth / slice_thickness.m_as("m") / system_specs.gamma.m_as("1/mT/ms")
        return amp_for_rf - x[1]

    cons = ({'type': 'eq', 'fun': _flat_dur},
            {'type': 'ineq', 'fun': lambda x: x[0]},
            {'type': 'ineq', 'fun': lambda x: x[1]},
            {'type': 'ineq', 'fun': lambda x: -x[1] + system_specs.max_grad.m_as("mT/m")},
           )

    if min_duration is not None:
        cons = cons + ({'type': 'ineq', 'fun': lambda x: x[0] - min_duration.m_as("ms")}, )

    # initial guess
    shortest_pulse = cmrseq.bausteine.SincRFPulse.from_shortest(
                                                system_specs=system_specs,
                                                flip_angle=Quantity(45, "degree"),
                                                time_bandwidth_product=time_bandwidth_product,
                                                center=0.5, name="dummy")
    shortest_bw = shortest_pulse.bandwidth.m_as("1/ms")
    shortest_grad_amp = (Quantity(shortest_bw, "1/ms") / slice_thickness
                         / system_specs.gamma).m_as("mT/m")
    initial_guess = [shortest_bw, shortest_grad_amp]

    # Call optimization
    res = minimize(fun=_optim, x0=initial_guess, constraints=cons)
    pulse_duration = system_specs.time_to_raster(Quantity(res.x[0], "ms"))
    bandwidth = time_bandwidth_product / pulse_duration
    gradient_amplitude = (bandwidth / slice_thickness / system_specs.gamma).to("mT/m")
    return pulse_duration, gradient_amplitude


def slice_selective_se_pulses(system_specs: 'cmrseq.SystemSpec',
                              echo_time: Quantity,
                              slice_thickness: Quantity,
                              pulse_duration: Quantity,
                              slice_orientation: np.ndarray,
                              time_bandwidth_product: float = 4.) -> cmrseq.Sequence:
    """ Define a pair of 90, 180 rf sinc pulses with slice selective gradients

    .. code-block::

                        |-----------echo_time/2---------|

       .                90°                            180°              .
       .                                                                 .
       .               /\                              /\                .
       .    _______/\ /  \ /\______________________/\ /  \ /\            .
       .            \/   \/                         \/   \/              .
       .                                                                 .
       .          ___________                      ___________           .
       .    ____ /           \       _____________/           \          .
       .                      \_____/                                    .
       .          |pulse-dur|                      |pulse-dur|           .


    :param system_specs: SystemSpecifications
    :param echo_time: Quantity[Time] containing the required echo-time
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param pulse_duration: Quantity[Time] Total pulse duration (corresponds to flat_duration of the
                            slice selection gradient)
    :param slice_orientation: np.ndarray of shape (3, ) denoting the direction of the slice-normal.
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :return:
    """
    excite = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
        system_specs=system_specs,
        slice_thickness=slice_thickness,
        flip_angle=Quantity(np.pi / 2, "rad"),
        pulse_duration=pulse_duration,
        time_bandwidth_product=time_bandwidth_product,
        delay=Quantity(0., "ms"),
        slice_normal=slice_orientation)

    excitation_center_time = excite.rf_events[0][0]
    refocus_delay = excitation_center_time - pulse_duration / 2 + echo_time / 2
    refocus = cmrseq.bausteine.SincRFPulse(system_specs=system_specs,
                                           flip_angle=Quantity(np.pi, "rad"),
                                           duration=pulse_duration,
                                           time_bandwidth_product=time_bandwidth_product,
                                           center=0.5,
                                           delay=refocus_delay,
                                           name="rf_refocus")
    ss_grad = excite.get_block("slice_select_0")
    sliceselect_refocus = cmrseq.bausteine.TrapezoidalGradient(
                                                   system_specs, slice_orientation,
                                                   ss_grad.magnitude, pulse_duration,
                                                   ss_grad.rise_time,
                                                   delay=refocus.tmin - ss_grad.rise_time,
                                                   name="slice_select_refocus")

    seq = excite + cmrseq.Sequence([refocus, sliceselect_refocus], system_specs=system_specs)
    return seq


def spectral_spatial_excitation(system_specs: cmrseq.SystemSpec, binomial_degree: int,
                                total_flip_angle: Quantity, slice_thickness: Quantity,
                                chemical_shift: float = 3.4,
                                time_bandwidth_product=4.5) -> cmrseq.Sequence:
    """Constructs a sequence for spectral-spatial excitation containing binomial sinc sub-pulses
    and trapezoidal slice-selection gradients. The suppressed frequency is defined as chemical
    shift (with B0 from the system-specification), which determines the temporal gap between
    the sub-pulses. Feasibility of the pulse composition is checked based on gradient limits
    and peak rf power.

    .. note::

        The effective rf center can be obtained as the mean of all sub-pulse rf centers

    The sub-pulse duration is calculated under the assumption of max slew gradient as follows:

    .. math::

        & \\tau      = 1/(2CS * B_0 \gamma *1e-6) \\\\
        & \\tau / 2  = 2 \delta + T  \\\\
        & T = tbw / (\gamma \delta s_{max} \Delta z) \\\\
        & \\rightarrow 0 =& 4 \\delta^2 - \\tau \\delta + 2 tbw /(\gamma \\Delta z s_{max}) \\\\
        & \\rightarrow \\delta = \\tau \pm \sqrt{\\tau ^2 - 32 tbw/ \gamma \\Delta z s_{max}})/8\\\\

    where :math:`\tau` is gap between sub-pulses, :math:`CS` is the chemical shift in ppm,
    :math:`delta` is the rise time of the trapezoidal gradient, :math:`\Delta` is the pulse/flat top
    duration and :math:`s_{max}` is the system limit for gradient slew-rate.

    .. Dropdown:: Example Plots
        :animate: fade-in-slide-down
        :icon: graph
        :color: secondary

        .. image:: ../_static/api/seqdefs_excitation_spectral_spatial.png

    :raises: - ValueError: if the pulse is infeasible for system-constrains / slice-thickness /
                    time-bandwidth-product because the minimal pulse duration + gradient
                    ramp-times is shorter than half of the pulse gap

    :param system_specs:
    :param binomial_degree: Determines the number of sub-pulses. Degree 1 corresponds to 1-1,
            degree 2 -> 1-2-1 and so on.
    :param total_flip_angle: Total effective flip angle for on-resonant spins for all
                sub-pulses combined
    :param slice_thickness: Thickness of spatial excitation slab. For very thin slices, the targeted
            pulse might become infeasible
    :param chemical_shift: in parts per milion
    :param time_bandwidth_product: Time bandwidth product used for all sinc sub-pulses
    :return:
    """

    binomial_coeffs = np.array(
        [math.factorial(binomial_degree) // math.factorial(y) // math.factorial(binomial_degree - y)
         for y in range(binomial_degree + 1)])
    subpulse_flip_angles = total_flip_angle.to("degree") * binomial_coeffs / np.sum(binomial_coeffs,
                                                                                    keepdims=True)

    chemical_shift_freq = system_specs.gamma * system_specs.b0 * chemical_shift * 1e-6
    pulse_gap = system_specs.time_to_raster((1 / 2 / chemical_shift_freq.to("Hz")).to("ms"), "grad")

    # Check if pulses are feasible
    max_sub_fa = np.max(subpulse_flip_angles)
    max_pulse_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                                    system_specs,
                                                    slice_thickness=slice_thickness,
                                                    flip_angle=max_sub_fa,
                                                    time_bandwidth_product=time_bandwidth_product)

    if pulse_gap / 2 < max_pulse_seq.get_block("slice_select_0").duration:
        max_tbw = pulse_gap.to("ms") ** 2 * (
                    system_specs.gamma * slice_thickness * system_specs.max_slew).to("1/ms**2") / 32
        min_slth = (32 * time_bandwidth_product / (
                    pulse_gap ** 2 * system_specs.gamma * system_specs.max_slew)).m_as("mm")
        raise ValueError(
            f"Pulse not feasible for given system limits! Try increasing the slice"
            f" thickness > {min_slth: 1.3}mm or decreasing the "
            f"time-bandwidth-product < {max_tbw.m * 0.9: 1.4}.")

        # print(max_pulse_seq.get_block("rf_excitation_0").duration)
    # Solve quadratic equation from docstring to obtain ramptime and subsequently pulse duration
    a = 4
    b = - pulse_gap
    c = 2 * time_bandwidth_product / (system_specs.gamma * slice_thickness * system_specs.max_slew)
    radicant = b ** 2 - 4 * a * c
    ramp_dur_p = (- b + np.sqrt(radicant)) / (2 * a)
    ramp_dur_m = (- b - np.sqrt(radicant)) / (2 * a)
    ramp_dur = system_specs.time_to_raster(
        np.min(np.stack([r for r in (ramp_dur_p, ramp_dur_m) if r > Quantity(0, "ms")])), "grad")
    flat_dur = system_specs.time_to_raster((pulse_gap - 4 * ramp_dur) / 2, "grad")

    seqs = []
    for pulse_idx, fa in enumerate(subpulse_flip_angles):
        temp_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                                    system_specs,
                                                    slice_thickness=slice_thickness,
                                                    flip_angle=fa,
                                                    pulse_duration=flat_dur,
                                                    time_bandwidth_product=time_bandwidth_product)
        if pulse_idx < len(subpulse_flip_angles) - 1:
            temp_seq.remove_block("slice_select_rewind_0")
            temp_block = deepcopy(temp_seq.get_block("slice_select_0"))
            temp_block.scale_gradients(-1)
            temp_seq.append(temp_block)
        seqs.append(temp_seq)
    result_seq_obj = seqs[0]
    result_seq_obj.extend(seqs[1:])

    return result_seq_obj
