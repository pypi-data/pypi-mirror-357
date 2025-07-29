""" This module contains parametric definitions of complete multi-TR GRE-based sequences"""
__all__ = ["flash", "radial_flash"]

from warnings import warn
from typing import List

import numpy as np
from pint import Quantity
from copy import deepcopy

import cmrseq


# pylint: disable=R0913, R0914
def flash(system_specs: cmrseq.SystemSpec,
          matrix_size: np.ndarray,
          inplane_resolution: Quantity,
          slice_thickness: Quantity,
          adc_duration: Quantity,
          flip_angle: Quantity,
          pulse_duration: Quantity,
          repetition_time: Quantity,
          echo_time: Quantity,
          slice_position_offset: Quantity = Quantity(0., "m"),
          time_bandwidth_product: float = 4.,
          dummy_shots: int = 0,
          fuse_slice_rewind_and_prephaser: bool = True,
          rf_spoil: bool = True) -> List[cmrseq.Sequence]:
    """ Defines a 2D gradient echo sequence.

    :param system_specs: SystemSpecifications
    :param matrix_size: array of shape (2, ) containing the resulting matrix dimensions
    :param inplane_resolution: Quantity[Length] of shape (2, ) containing the in-plane
                                voxel dimensions
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param repetition_time: Quantity[Time] containing the required repetition_time
    :param echo_time: Quantity[Time] containing the required echo-time. If too short for
                    given system specifications, it is increased to minimum and a warning is raised.
    :param flip_angle: Quantity[Angle] containing the required flip_angle
    :param pulse_duration: Quantity[Time] Total pulse duration (corresponds to flat_duration of the
                            slice selection gradient)
    :param slice_position_offset: Quantity[Length] positional offset in slice normal direction
                                  defining the frequency offset of the RF pulse
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :param dummy_shots: number of dummy shots (TRs) without adc-events, with k-space center
                        phase encoding
    :param fuse_slice_rewind_and_prephaser: If True, the slice selection rewinder is recalculated
                to match the duration of the prephaser, resulting in the fastest possible 3D k-space
                traverse.
    :param rf_spoil: If True, the RF phase is incremented for each TR to achieve spoiling, according to Zur et al (1991)
    :return: List of sequence objects, that each represent a single TR
    """
    
    # Step 0: Create a slice-selective excitation
    rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
                                    system_specs=system_specs,
                                    slice_thickness=slice_thickness,
                                    flip_angle=flip_angle,
                                    pulse_duration=pulse_duration,
                                    time_bandwidth_product=time_bandwidth_product,
                                    slice_position_offset=slice_position_offset,
                                    slice_normal=np.array([0., 0., 1.]))
    ss_refocus = rf_seq["slice_select_rewind_0"]
    
    # Step 1: Determine ADC-duration 
    k_max_inplane, _, kro_traverse = cmrseq.seqdefs.readout.matrix_to_kspace_2d(matrix_size, inplane_resolution)

    if echo_time is not None: # Case 1: Echo time is defined

        if adc_duration is None: # ADC is not defined, so we try to find the longest possible
            # Time between TE and end of RF slice select gradient
            time_to_fill = echo_time - (rf_seq['slice_select_0'].duration - rf_seq['rf_excitation_0'].rf_events[0])

            if fuse_slice_rewind_and_prephaser:
                add_k_traverse = Quantity([k_max_inplane[1].m_as("1/m"), 
                                        (ss_refocus.area[-1] * system_specs.gamma).m_as("1/m")],
                                        "1/m")
            else:
                # In this case, we leave the ss refocus gradient as is
                time_to_fill = time_to_fill - ss_refocus.duration
                add_k_traverse = Quantity([k_max_inplane[1].m_as("1/m"), 0.], "1/m")
                
            try:
                # We can use a trick here to ensure we get the right TE
                # We use double the available time to fill, and use the balanced variant
                # Since for balanced TE is at the center (symmetric) this solved for the optimal gradients up to TE
                prephaser, _, adc = cmrseq.seqdefs.readout.get_longest_adc_duration(
                                                    system_specs, time_to_fill, 
                                                    matrix_size[0], inplane_resolution[0],
                                                    balanced=True,
                                                    additional_kspace_traverse=add_k_traverse)
                internal_adc_duration = adc.duration
            except:
                # Something went wrong, likely the time to fill is not feasible, so we resort the same as case 2
                _, adc = cmrseq.seqdefs.readout.get_shortest_adc_duration(
                                            system_specs, matrix_size[0], inplane_resolution[0])
                internal_adc_duration = adc.duration
        else:
            internal_adc_duration = adc_duration

    else: # Case 2: Echo time is not defined, so we try to minimize it
        if adc_duration is None: # ADC is not defined
            # This is a trivial case, since we can just use the shortest possible ADC duration and TE is whatever we get
            _, adc = cmrseq.seqdefs.readout.get_shortest_adc_duration(system_specs, matrix_size[0], inplane_resolution[0])
            internal_adc_duration = adc.duration
        else:
            internal_adc_duration = adc_duration

    # Step 2: Compute prephaser duration

    # Get example readout gradient
    ro_dummy = cmrseq.seqdefs.readout.balanced_gre_cartesian_line(system_specs, matrix_size[0], 
                                                    kro_traverse, k_max_inplane[1],
                                                    internal_adc_duration)
    ro_dummy_trap = ro_dummy["trapezoidal_readout_0"]
    ro_dummy_prephaser = ro_dummy["ro_prephaser_0"]

    if fuse_slice_rewind_and_prephaser:

        # Get fastest possible prephaser
        k_max_x = (ro_dummy_prephaser.area[0] * system_specs.gamma).m_as("1/m")
        k_max_y = k_max_inplane[1].m_as("1/m")
        kz_refocus = (ss_refocus.area * system_specs.gamma).m_as("1/m")
        total_kspace_traverse = Quantity([k_max_x, k_max_y, kz_refocus[-1]], "1/m")
        _, _rise, _flat = system_specs.get_fastest_kspace_traverse(total_kspace_traverse)

        if echo_time is not None:
            # Echo time is defined, so we use prephased to fill the gap
            max_prephaser_duration = echo_time - (ro_dummy_trap.duration/2 + rf_seq['slice_select_0'].duration - rf_seq['rf_excitation_0'].rf_events[0])
            max_prephaser_duration = system_specs.time_to_raster(max_prephaser_duration, "grad")

            if max_prephaser_duration < _flat + 2*_rise:
                raise ValueError("Echo time is too short or ADC duration is too long")
            
            # Get prephaser gradient
            combined_gradient_area = Quantity(np.linalg.norm(total_kspace_traverse.m_as("1/m")), "1/m") / system_specs.gamma.to("1/mT/ms")
            prephaser_total = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs=system_specs,
                                                                                orientation=np.array([1., 0., 0.]),
                                                                                duration=max_prephaser_duration,
                                                                                area=combined_gradient_area)
        
            _flat = prephaser_total.flat_duration
            _rise = prephaser_total.rise_time
        prephaser_duration = _flat + 2*_rise
    else:
        # No fusing, but might need to add a delay
        prephaser_duration = ro_dummy_prephaser.duration
        if echo_time is not None:
            max_prephaser_duration = echo_time - (ro_dummy_trap.duration/2 + rf_seq['slice_select_0'].duration - rf_seq['rf_excitation_0'].rf_events[0])
            max_prephaser_duration = system_specs.time_to_raster(max_prephaser_duration, "grad")

            if ro_dummy_prephaser.duration + ss_refocus.duration > max_prephaser_duration:
                raise ValueError("Echo time is too short or ADC duration is too long. Try fuse_slice_rewind_and_prephaser=True ")

            prephaser_delay = max_prephaser_duration - prephaser_duration - ss_refocus.duration
            if np.isclose(prephaser_delay.m_as('ms'), 0., atol=1e-10):
                prephaser_delay = Quantity(0., 'ms')
        else:
            prephaser_delay = Quantity(0., 'ms')

    # Step 3: Create readout blocks
    ro_blocks = cmrseq.seqdefs.readout.multi_line_cartesian(system_specs=system_specs,
                                                            fnc=cmrseq.seqdefs.readout.gre_cartesian_line,
                                                            matrix_size=matrix_size,
                                                            inplane_resolution=inplane_resolution,
                                                            adc_duration=internal_adc_duration,
                                                            prephaser_duration=prephaser_duration,
                                                            dummy_shots=dummy_shots)

    # Step 4: Check TR and add delay if needed. If too short, override
    tr_delay = Quantity(0,'ms')
    if repetition_time is not None:
        if fuse_slice_rewind_and_prephaser:
            minimal_tr = ro_blocks[0].get_block("trapezoidal_readout_0").duration + rf_seq.duration - ss_refocus.duration + prephaser_duration
        else:
            minimal_tr = ro_blocks[0].get_block("trapezoidal_readout_0").duration + rf_seq.duration + prephaser_duration

        if minimal_tr > system_specs.time_to_raster(repetition_time,"grad"):
            warn(f"Repetition time too short to be feasible, set TR to {minimal_tr}")
            repetition_time = minimal_tr
        
        tr_delay = system_specs.time_to_raster(repetition_time,"grad") - minimal_tr
        if np.isclose(tr_delay.m_as('ms'), 0., atol=1e-10):
            tr_delay = Quantity(0., 'ms')

    # Step 5: Re-generate SS rewind and readout prephaser if fusing 
    if fuse_slice_rewind_and_prephaser:
        ss_rewind_amp = ss_refocus.area[-1]/(_flat + _rise)
        ss_rewind = cmrseq.bausteine.TrapezoidalGradient(system_specs,
                                                np.array([0., 0., -1.]),
                                                flat_duration=_flat,
                                                rise_time=_rise,
                                                amplitude=ss_rewind_amp,
                                                name="slice_select_rewind")
        
        ro_prephaser_amp = ro_blocks[0]['ro_prephaser_0'].area[0]/(_flat + _rise)
        ro_prephaser = cmrseq.bausteine.TrapezoidalGradient(system_specs,
                                                np.array([-1., 0., 0.]),
                                                flat_duration=_flat,
                                                rise_time=_rise,
                                                amplitude=ro_prephaser_amp,
                                                name="ro_prephaser")

    # Step 6: Build sequence
    seq_list = []
    
    phase_offset = Quantity(0, 'degree')
    pi_phase = Quantity(360, 'degree')
    # Zur et al (1991)
    rf_incr = Quantity(117, 'degree')

    for j, ro_b in enumerate(ro_blocks):
        
        seq = deepcopy(rf_seq)
        # RF spoiling
        if rf_spoil:
            seq['rf_excitation_0'].phase_offset = phase_offset
            if ro_b.get_block('adc_0') is not None:
                ro_b.get_block('adc_0').phase_offset = phase_offset

            phase_offset = (phase_offset + rf_incr) % pi_phase
        
        if fuse_slice_rewind_and_prephaser:
            # Produce new pe prephaser and replace all prephasers
            pe_prephaser_amp = ro_b['pe_prephaser_0'].area[1]/(_flat + _rise)
            dir_norm = np.sqrt(np.sum(ro_b['pe_prephaser_0'].gradients[1][:,1]**2))
            if not dir_norm == 0:
                pedir = (ro_b['pe_prephaser_0'].gradients[1][:,1] / dir_norm).m_as("dimensionless")
            else:
                pedir = np.array([0., 1., 0.])
            pe_prephaser = cmrseq.bausteine.TrapezoidalGradient(system_specs,
                                                    pedir,
                                                    flat_duration=_flat,
                                                    rise_time=_rise,
                                                    amplitude=pe_prephaser_amp,
                                                    name="pe_prephaser")
            
            ro_b.remove_block("pe_prephaser_0")
            ro_b.remove_block("ro_prephaser_0")
            seq.remove_block("slice_select_rewind_0")

            ro_b.add_block(ro_prephaser)
            ro_b.add_block(pe_prephaser)
            ro_b.add_block(ss_rewind)
        else:
            # Add the prephaser delay to the sequence
            if prephaser_delay > 0:  
                seq.append(cmrseq.bausteine.Delay(system_specs, prephaser_delay))

        seq.append(ro_b)
        # Add TR delay if needed
        if tr_delay > 0:
            seq.append(cmrseq.bausteine.Delay(system_specs, tr_delay))
        seq_list.append(seq)
    return seq_list


def radial_flash(system_specs: cmrseq.SystemSpec,
                 samples_per_spoke: int,
                 inplane_resolution: Quantity,
                 slice_thickness: Quantity,
                 adc_duration: Quantity,
                 flip_angle: Quantity,
                 pulse_duration: Quantity,
                 repetition_time: Quantity,
                 echo_time: Quantity,
                 spoke_angle_increment: Quantity = None,
                 num_spokes: int = None,
                 slice_position_offset: Quantity = Quantity(0., "m"),
                 time_bandwidth_product: float = 4.,
                 dummy_shots: int = 0,
                 fuse_slice_rewind_and_prephaser: bool = True) -> List[cmrseq.Sequence]:
    
    """Defines a 2D radial FLASH sequence. Not as optimized as cartesian FLASH.

    :param system_specs: SystemSpecification
    :param samples_per_spoke: number of samples per spoke, i.e. number of adc-events per TR
    :param inplane_resolution: Isotropic in-plane resolution, defines max kspace radius. Quantity[Length]
    :param slice_thickness: Quantity[Length] containing the required slice-thickness
    :param adc_duration: Quantity[time] Total duration of adc-sampling for a single TR
    :param flip_angle: Quantity[Angle] containing the required flip_angle
    :param pulse_duration: Quantity[Time] Total pulse duration (corresponds to flat_duration of the
                            slice selection gradient)
    :param repetition_time: Quantity[Time] containing the desired repetition time 
    :param echo_time: Quantity[Time] containing the desired echo time
    :param spoke_angle_increment: Quantity[Angle] angle increment between spokes, if None, sets to uniformly fill 2pi
    :param num_spokes: number of spokes to acquire, if None, if None, defaults to satisfy nyquist
    :param slice_position_offset: Quantity[Length] positional offset in slice normal direction
                              defining the frequency offset of the RF pulse
    :param time_bandwidth_product: float - used to calculate the rf bandwidth from duration
    :param dummy_shots: number of shots(TRs) without adc-events before starting the acquisition
    :param fuse_slice_rewind_and_prephaser: If True, the slice selection rewinder is recalculated
            to match the duration of the prephaser, resulting in the fastest possible 3D k-space
            traverse.
    :return: List of length (n_dummy+matrix_size[1]) containting one Sequence object per TR
    """

    rf_seq = cmrseq.seqdefs.excitation.slice_selective_sinc_pulse(
        system_specs=system_specs,
        slice_thickness=slice_thickness,
        flip_angle=flip_angle,
        pulse_duration=pulse_duration,
        time_bandwidth_product=time_bandwidth_product,
        slice_position_offset=slice_position_offset,
        slice_normal=np.array([0., 0., 1.]))
    ss_refocus = rf_seq.get_block("slice_select_rewind_0")

    kr_max = 1 / (2 * inplane_resolution.m_as("m"))

    if fuse_slice_rewind_and_prephaser:
        # Recalculate ss-gradient combined with ro prephaser

        kz_refocus = (ss_refocus.area * system_specs.gamma).m_as("1/m")

        total_kspace_traverse = Quantity(np.linalg.norm([kr_max, kz_refocus[-1]]), "1/m")
        combined_gradient_area = total_kspace_traverse / system_specs.gamma.to("1/mT/ms")
        prephaser_duration = cmrseq.bausteine.TrapezoidalGradient.from_area(
            system_specs, np.array([1., 0., 0]), combined_gradient_area).duration

        rf_seq.remove_block("slice_select_rewind_0")
        ss_refocus = cmrseq.bausteine.TrapezoidalGradient.from_dur_area(system_specs,
                                                                        np.array([0., 0., -1.]),
                                                                        prephaser_duration,
                                                                        ss_refocus.area[-1],
                                                                        delay=rf_seq.duration,
                                                                        name="slice_select_rewind")
        rf_seq.add_block(ss_refocus)
    else:
        prephaser_duration = None

    ro_ref = cmrseq.seqdefs.readout.radial_spoke(system_specs=system_specs, num_samples=samples_per_spoke,
                                                 kr_max=Quantity(kr_max,'1/m'), angle=Quantity(0, 'rad'),
                                                 adc_duration=adc_duration,
                                                 prephaser_duration=prephaser_duration)

    dummy_ref = cmrseq.seqdefs.readout.radial_spoke(system_specs=system_specs, num_samples=0,
                                                    kr_max=Quantity(kr_max,'1/m'), angle=Quantity(0, 'rad'),
                                                    adc_duration=adc_duration,
                                                    prephaser_duration=prephaser_duration)

    if prephaser_duration is None:
        prephaser_duration = ro_ref.get_block("radial_prephaser_0").duration

    readout_gradient_duration = ro_ref.get_block("radial_readout_0").duration
    max_ssref_prephaser = max(ss_refocus.duration, prephaser_duration)
    adc_center = system_specs.time_to_raster(ro_ref.get_block('adc_0').adc_center)

    if fuse_slice_rewind_and_prephaser:
        minimal_tr = readout_gradient_duration + max_ssref_prephaser + rf_seq.duration - ss_refocus.duration
        minimal_te = (rf_seq.duration - rf_seq.get_block("rf_excitation_0").rf_events[0] - ss_refocus.duration +
                      max_ssref_prephaser + adc_center - prephaser_duration)
    else:
        minimal_tr = ro_ref.duration + rf_seq.duration
        minimal_te = (rf_seq.duration - rf_seq.get_block("rf_excitation_0").rf_events[0] + adc_center)


    repetition_time = system_specs.time_to_raster(repetition_time)
    if repetition_time < minimal_tr:
        warn(f"Radial FLASH Sequence: Repetition time too short to be feasible, set TR to {minimal_tr}")
        repetition_time = minimal_tr

    maximum_te = repetition_time - (readout_gradient_duration - adc_center + prephaser_duration) \
                 - rf_seq.get_block("rf_excitation_0").rf_events[0]

    echo_time = system_specs.time_to_raster(echo_time)
    if echo_time < minimal_te:
        warn(f"Radial FLASH Sequence: Echo time too short to be feasible, set TE to {minimal_te}")
        echo_time = minimal_te

    if echo_time > maximum_te:
        warn(f"Radial FLASH Sequence: Echo time too long for given TR, set TE to {maximum_te}")
        echo_time = maximum_te

    te_shift = echo_time - minimal_te
    tr_delay = repetition_time - minimal_tr - te_shift

    # Concatenate readout blocks
    seq_list = []

    for _ in range(dummy_shots):
        cur_ro = deepcopy(dummy_ref)
        if fuse_slice_rewind_and_prephaser:
            cur_ro.shift_in_time(
                rf_seq.duration - min(ss_refocus.duration, prephaser_duration) + te_shift)
        else:
            cur_ro.shift_in_time(
                rf_seq.duration + te_shift)
        seq = rf_seq + cur_ro
        seq.append(cmrseq.bausteine.Delay(system_specs, tr_delay))
        seq_list.append(seq)

    if num_spokes is None:
        if spoke_angle_increment is not None:
            warn(f"Radial FLASH Sequence: Can not set spoke angle increment without "
                 f"setting number of spokes, defaulting to satisfy nyquist")

        num_spokes = np.ceil(samples_per_spoke*np.pi/2) # Nyquist criteria for radial sampling

        spoke_angles = np.linspace(0,np.pi,int(num_spokes),endpoint=False)
    else:
        if spoke_angle_increment is None:
            warn(f"Radial FLASH Sequence: Spoke angle not set while spoke count set,"
                 f" defaulting to even spacing of spokes")
            spoke_angles = np.linspace(0,np.pi,int(num_spokes),endpoint=False)
        else:
            spoke_angles = np.array(range(num_spokes))*spoke_angle_increment.to('rad').m_as('dimensionless')

    for angle in spoke_angles:
        cur_ro = deepcopy(ro_ref)

        sa = np.sin(angle)
        ca = np.cos(angle)
        omatrix = cmrseq.OMatrix(system_specs=system_specs,
                            position=Quantity(0,'m'),
                            slice_normal=np.array([0,0,1]),
                            readout_direction = np.array([ca,sa,0]))
        cur_ro.register_omatrix(matrix=omatrix, gradients=seq.blocks)

        if fuse_slice_rewind_and_prephaser:
            cur_ro.shift_in_time(
                rf_seq.duration - min(ss_refocus.duration, prephaser_duration) + te_shift)
        else:
            cur_ro.shift_in_time(
                rf_seq.duration + te_shift)
        seq = rf_seq + cur_ro
        seq.append(cmrseq.bausteine.Delay(system_specs, tr_delay))
        seq_list.append(seq)

    return seq_list
