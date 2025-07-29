""" Utility module contains helpers functions."""
__all__ = ["find_gradient_blocks", "grid_sequence_list",
           "calculate_gradient_spectra", "concomitant_fields"]

from typing import List, Tuple
from copy import deepcopy

from pint import Quantity
import numpy as np
import scipy.integrate

from cmrseq import Sequence

def find_gradient_blocks(time_points: np.ndarray, grad_wf: np.ndarray) \
        -> List[Tuple[str, np.ndarray, np.ndarray]]:
    """Given an array of single-channel gradient amplitudes (waveform) and
    corresponding time points, subdivides the waveform into possible trapezoidal
    and arbitrary gradient definitions.

    Assumes that for consecutive trapezoids, the zero-crossing is explicitly included,
    otherwise the two lobes are combined into one arbitrary waveform. Trapezoids,
    include triangular gradient pulses. Zero-crossings of arbitrary gradients
    (such as spirals) are not used to subdivide the shape.

    .. note::

        Comparison by value of inflection points and slew-rates are done up to the
        precision on 1e-8, therefore it is advisable to adhere to the stated units
        or scale correspondingly!

    :param time_points: (t, ) array of time-points in ms
    :param grad_wf: (t, ) array of gradient-waveforms in mT/m
    :return: Temporally ordered gradient definitions containing:
            - the type (trapezoid/arbitrary)
            - the time-points (t_i,)
            - the gradient samples (g_i, )
    """

    # ToDo: adjust atol throughout cmrseq - 8 digits need atol 1e-7
    if not (start_end_zero := np.allclose([grad_wf[0], grad_wf[-1]], 0., atol=1e-7)):
        raise ValueError("find_gradient_blocks assumes the gradient waveform to start AND and "
                         "with a zero amplitude", start_end_zero)

    slew_rate = np.diff(grad_wf, prepend=0.) / np.diff(time_points, prepend=1)

    from collections import deque
    def_que = deque()
    t_que = deque()
    slew_que = deque()

    def _popleft_def(n_samples: int) -> (np.ndarray, np.ndarray):
        t_def = np.array([t_que.popleft() for _ in range(n_samples)])
        grad_def = np.array([def_que.popleft() for _ in range(n_samples)])
        _ = [slew_que.popleft() for _ in range(n_samples)]
        slew_que.appendleft(0.)
        def_que.appendleft(grad_def[-1])
        t_que.appendleft(t_def[-1])
        return t_def, grad_def

    def _popright_def(n_samples: int) -> (np.ndarray, np.ndarray):
        t_def = np.array([t_que.pop() for _ in range(n_samples)][::-1])
        grad_def = np.array([def_que.pop() for _ in range(n_samples)][::-1])
        _ = [slew_que.pop() for _ in range(n_samples)]
        slew_que.clear()
        slew_que.append(0.)
        def_que.append(grad_def[0])
        t_que.append(t_def[0])
        return t_def, grad_def


    def_que.append(grad_wf[0])
    t_que.append(time_points[0])
    slew_que.append(slew_rate[0])
    gradient_definitions: List[(str, np.ndarray, np.ndarray)] = []
    for idx, (t, samp, slew) in enumerate(zip(time_points[1:], grad_wf[1:], slew_rate[1:])):

        # If slew is the same as the last step, the last point can be omitted as redundant
        if np.isclose(slew, slew_que[-1], atol=1e-6):
            def_que.pop()
            t_que.pop()
            slew_que.pop()

        def_que.append(samp)
        t_que.append(t)
        slew_que.append(slew)

        # Necessary condition to check for a completed gradient shape, is
        # defined by: starts and ends at zero. Otherwise, continue queueing
        # more samples
        if np.allclose([def_que[0], def_que[-1]], 0., atol=1e-8):
            # Trivial case means redundant zeros -> remove consecutive zeros
            if len(def_que) == 2:
                def_que.popleft()
                t_que.popleft()
                slew_que.popleft()
            # Trapezoidal including triangular can be defined with 3 or 4 samples.
            # If Pop trapezoid def and append to found blocks.
            elif len(def_que) == 3:
                gradient_definitions.append(("trapezoid", *_popleft_def(3)))
            elif (len(def_que) == 4 and
                  np.isclose(def_que[-3], def_que[-2], atol=1e-8)):
                gradient_definitions.append(("trapezoid", *_popleft_def(4)))
            # To allow zero-crossings in arbitrary waveforms, we look ahead one sample.
            # If it is zero we pop the shape. However, this would not match the case of
            # a trapezoidal definition directly following an arbitrary waveform.
            # Therefore, we need to check if the last three or four samples constitute a
            # trapezoidal gradient.
            elif len(def_que) > 4:
                if np.allclose([def_que[-3], def_que[-1]], 0., atol=1e-8):
                    trap_def = _popright_def(3)
                    arb_def = _popleft_def(len(t_que))
                    gradient_definitions.append(("arbitrary", *arb_def))
                    gradient_definitions.append(("trapezoid", *trap_def))
                elif (np.allclose([def_que[-4], def_que[-1]], 0., atol=1e-8)
                      and np.isclose(def_que[-3], def_que[-2], atol=1e-8)):
                    trap_def = _popright_def(4)
                    arb_def = _popleft_def(len(t_que))
                    gradient_definitions.append(("arbitrary", *arb_def))
                    gradient_definitions.append(("trapezoid", *trap_def))
                # If next sample is not zero, we assume the arbitrary waveform is still continuing
                # Otherwise pop the entire waveform
                if idx == len(time_points) - 2 or np.isclose(grad_wf[idx+1], 0., atol=1e-8):
                    gradient_definitions.append(("arbitrary", *_popleft_def(len(t_que))))

    return gradient_definitions

# pylint: disable=C0103
def grid_sequence_list(sequence_list: List[Sequence],
                       force_uniform_grid: bool = False) \
        -> Tuple[List[np.ndarray], ...]:
    """ Grids RF, Gradients and adc_events of all sequences in the provided List.

    :param sequence_list:
    :param force_uniform_grid: bool if False the ADC-events are inserted into the time grid
                resulting in a non-uniform raster per TR
    :return: (time, rf_list, wf_list, adc_list)
    """
    time_list, rf_list, grad_list, adc_list = [], [], [], []
    for seq in sequence_list:
        rf, wf, adc_info = None, None, None
        if len(seq.rf) > 0:
            time_rf, rf = seq.rf_to_grid()
            time = time_rf
        if len(seq.gradients) > 0:
            time_grad, wf = seq.gradients_to_grid()
            wf = wf.T
            time = time_grad
        if len(seq.adc_centers) > 0:
            t_adc, adc_on, adc_phase, start_end = seq.adc_to_grid(force_raster=force_uniform_grid)
            adc_info = np.stack([adc_on, adc_phase], axis=-1)

        if 'start_end' in locals():
            if force_uniform_grid:
                adc_on[start_end[0, 0]:start_end[0, 1]] = 1
            else:
                if len(seq.gradients) > 0:
                    wf = np.stack([np.interp(t_adc, time_grad, g) for g in wf.T], axis=-1)
                if len(seq.rf) > 0:
                    rf = np.interp(t_adc, time_rf, rf)
                time = t_adc

        rf_list.append(rf)
        grad_list.append(wf)
        adc_list.append(adc_info)
        time_list.append(time)

    return time_list, rf_list, grad_list, adc_list


def calculate_gradient_spectra(sequence: Sequence,
                               directions: List[np.ndarray],
                               start_time: Quantity = None,
                               end_time: Quantity = None,
                               interpolation_subfactor: int = 1,
                               pad_factor: int = 10):
    """ Calculates gradient sampling spectra along a given direction according to:

    .. math::

        S(\\omega,t) = |\\tilde{q}(\\omega,t)|^2

        \\tilde{q}(\\omega,t) = \\int_{0}^{t}q(t')e^{i\\omega t'}dt'

        q(t) = \\gamma \\int_{0}^{t}G(t')dt'

    where G(t) is the gradient. Spectra returns in units of :math:`mT^2/m^2/ms^4`

    :param sequence: Sequence to calculate spectra on
    :param directions: List[np.ndarray of shape (3, )] denoting the directions to calculate
                        spectra along
    :param start_time: Quantity[Time] Start time of spectra calculation window
    :param end_time: Quantity[Time] End time of spectra calculation window
    :param interpolation_subfactor: int, factor to divide sequence raster time by for
                spectra calculation
    :param pad_factor: int, multiplicative pad factor prior to fourier transform. Used to better
                resolve low frequencies
    :return: (List[Spectra],Frequency) Tuple of arrays giving spectra and frequency axis
    """

    seq = deepcopy(sequence)

    # In some cases we want finer gradient raster in order to produce
    # smoother/better resolved spectra
    if interpolation_subfactor > 1: interpolation_subfactor = 1
    seq._system_specs.grad_raster_time = seq._system_specs.grad_raster_time / interpolation_subfactor

    # normalize direction
    # direction = direction / np.linalg.norm(direction)

    # get gradients
    time, gradients = seq.gradients_to_grid()

    # project along dimension
    # gradients = np.sum((gradients * np.expand_dims(direction, 1)), axis=0))

    # MPS directions
    gm = gradients[0]
    gp = gradients[1]
    gs = gradients[2]

    # Get start and end indices
    if end_time is None:
        end_ind = -1
    else:
        end_ind = np.argmin(np.abs(time - end_time.m_as('ms'))) + 1

    if start_time is None:
        start_ind = 0
    else:
        start_ind = np.argmin(np.abs(time - start_time.m_as('ms')))

    # Perform spectra calculation of MPS directions as a basis
    # M
    qtm = np.cumsum(gm[start_ind:end_ind]) * seq._system_specs.grad_raster_time.m_as(
        'ms')  # mT/m*ms
    qtm_pad = np.pad(qtm, (np.shape(qtm)[0] * pad_factor, np.shape(qtm)[0] * pad_factor))
    qstm = np.fft.fft(qtm_pad) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms^2

    # P
    qtp = np.cumsum(gp[start_ind:end_ind]) * seq._system_specs.grad_raster_time.m_as(
        'ms')  # mT/m*ms
    qtp_pad = np.pad(qtp, (np.shape(qtp)[0] * pad_factor, np.shape(qtp)[0] * pad_factor))
    qstp = np.fft.fft(qtp_pad) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms^2

    # S
    qts = np.cumsum(gs[start_ind:end_ind]) * seq._system_specs.grad_raster_time.m_as(
        'ms')  # mT/m*ms
    qts_pad = np.pad(qts, (np.shape(qts)[0] * pad_factor, np.shape(qts)[0] * pad_factor))
    qsts = np.fft.fft(qts_pad) * seq._system_specs.grad_raster_time.m_as('ms')  # mT/m*ms^2

    # Linearly combine MPS basis for each direction, the calculate final spectra
    S_list = []
    for dir in directions:
        dir = dir / np.linalg.norm(dir)
        S = Quantity(np.abs(qstm * dir[0] + qstp * dir[1] + qsts * dir[2]) ** 2, 'mT^2/m^2*ms^4')
        S_list.append(S)

    freq = np.fft.fftfreq(qsts.shape[0], d=seq._system_specs.grad_raster_time.m_as('s'))

    return S_list, Quantity(freq, 'Hz')


def concomitant_fields(sequence: Sequence, coordinates: np.ndarray):
    """ Computes concomitant fields for all and accumulated phase for static positions at the end
    of the given sequence.

    .. math::

        B_c(t) = (g_z^2/(8B_0))(x^2 + y^2) + (g_x^2 + g_y^2)/(2 B_0)z^2 -
            (g_x g_z)/(2B_0) xz - (g_y g_z)/(2B_0)yz

        \phi_c(t) = \int_0^t \gamma / B_c(t\prime) dt\prime

    .. Dropdown:: References
        https://onlinelibrary.wiley.com/doi/abs/10.1002/%28SICI%291522-25
        94%28199901%2941%3A1%3C103%3A%3AAID-MRM15%3E3.0.CO%3B2-M?sid=nlm%3Apubmed

        https://pubmed.ncbi.nlm.nih.gov/22851517/

    :param sequence:
    :param coordinates: (..., [x, y, z])
    :return:
    """
    from tqdm import tqdm
    t, grads = sequence.gradients_to_grid()
    b0 = sequence._system_specs.b0.m_as("mT")
    gamma = sequence._system_specs.gamma.m_as("1/ms/mT") * np.pi * 2

    refocus_rf_times = [t_.m_as("ms") for (t_, fa) in sequence.rf_events
                        if fa == Quantity(180, "degree")]
    subdivision_indices = [0, ] + np.searchsorted(t, refocus_rf_times).tolist() + [-1, ]

    gy2gx2 = grads[1] ** 2 + grads[0] ** 2
    gz2 = grads[2] ** 2
    gxgz = grads[0] * grads[2]
    gygz = grads[1] * grads[2]

    phase = np.zeros(len(coordinates.reshape(-1, 3)))
    for left, right in zip(subdivision_indices[:-1], subdivision_indices[1:]):
        phase *= -1
        for idx, (x,y,z) in enumerate(tqdm(coordinates.reshape(-1, 3))):
            b_c = (gz2[left:right] / 4 * (x**2+y**2) + gy2gx2[left:right] * z**2 -
                   gxgz[left:right] * x * z - gygz[left:right] * y * z) / 2 / b0
            phi_ = scipy.integrate.trapezoid(b_c, x=t[left:right]) * gamma
            phase[idx] += phi_
    return phase.reshape(coordinates.shape[:-1])



