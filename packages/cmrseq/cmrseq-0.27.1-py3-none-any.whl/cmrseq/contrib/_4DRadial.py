
__all__ = ["gen_WASP"]

from typing import List
from copy import deepcopy

from pint import Quantity
import numpy as np
from tqdm.auto import tqdm

import cmrseq
import cmrseq.parametric_definitions

# Generates spoke angles for a 3D WASP radial trajectory
def gen_WASP(nspokes, nframes, polartilt=1, spiral_density=1 , rangefactor=1, random_seed=None):

    rang = rangefactor
    total_spokes = nspokes
    total_frames = nframes
    fmod = spiral_density
    scale = polartilt

    # Golden angle for spiral rotation
    golden = np.pi*(3-np.sqrt(5))


    proj_per_frame = int(np.ceil(nspokes/nframes))
    if np.mod(proj_per_frame,2)==1:
        proj_per_frame += 1
    # First calculate spokes for single spiral
    lspokes = int(proj_per_frame/2)

    
    #proj_per_frame = int(total_spokes/total_frames) # Spokes per spiral up-down (ie per pole tile)
    #lspokes = int(proj_per_frame/2) # Spokes per spiral 
    prev_angle=0

    fMODpar = fmod
    
    array_mp = np.zeros(lspokes+1) # z position of spoke
    array_ma = np.zeros(lspokes+1) # xy angle of spoke

    # Generate spiral template
    for i in range(lspokes+1):
        dh = -1 + 2 * i / lspokes / rang # goes from -1 to 1 (full sphere) or -1 to 0 (half sphere)
        array_mp[i] = np.arccos(dh) 
    
        if i==0 or (i==lspokes and rangefactor==1):
            array_ma[i] = 0 # set angle to zero at start and end
        else:
            array_ma[i] = np.mod(prev_angle + fMODpar / np.sqrt(lspokes * rang * (1 - dh ** 2)), 2 * np.pi)
    
        prev_angle = array_ma[i]

    # Generate arrays for full spirals (up and down)
    full_mp = np.zeros(proj_per_frame)
    full_ma = np.zeros(proj_per_frame)
    

    # Write out full spiral up down
    for i in range(lspokes):
    
        full_ma[i] = array_ma[i]
        full_mp[i] = array_mp[i]
    
        full_ma[i + lspokes] = array_ma[lspokes - i] + np.pi
        full_mp[i + lspokes] = array_mp[lspokes - i]

    
    # Rescale?
    lspokes = lspokes*2

    #polar rotation angle
    polar = 2*np.pi/np.sqrt(lspokes)*scale
    if random_seed != None:
        np.random.seed(random_seed)
    ran = np.random.uniform(0,1,(2,total_frames))

    # Generate polar tilting angles
    pol_x = np.zeros(total_frames)
    pol_y = np.zeros(total_frames)
    azi_z = np.zeros(total_frames)

    for i in range(total_frames):
        
        flip_polar = polar*ran[0,i]
        flip_phi = 2*np.pi*ran[1,i]
        pol_x[i] = flip_polar*np.sin(flip_phi)
        pol_y[i] = flip_polar*np.cos(flip_phi)
        azi_z[i] = (i+1)*golden


    # Transform spiral into x,y,z, coordinates
    x_b = np.zeros(proj_per_frame)
    y_b = np.zeros(proj_per_frame)
    z_b = np.zeros(proj_per_frame)
    
    for i in range(proj_per_frame):
        x_b[i] = np.sin(full_mp[i]) * np.cos(full_ma[i])
        y_b[i] = np.sin(full_mp[i]) * np.sin(full_ma[i])
        z_b[i] = np.cos(full_mp[i])


    # Rotate all each frame by polar tilting
    x = np.zeros((total_frames,proj_per_frame))
    y = np.zeros((total_frames,proj_per_frame))
    z = np.zeros((total_frames,proj_per_frame))
    
    for j in range(total_frames):
        for i in range(proj_per_frame):
            x_t = x_b[i]
            y_t = np.cos(pol_x[j])*y_b[i] + np.sin(pol_x[j])*z_b[i]
            z_t = -np.sin(pol_x[j]) * y_b[i] + np.cos(pol_x[j]) * z_b[i]
    
            x_i = np.cos(pol_y[j]) * x_t + np.sin(pol_y[j]) * z_t
            y_i = y_t
            z_i = -np.sin(pol_y[j]) * x_t + np.cos(pol_y[j]) * z_t
    
            x_t = np.cos(azi_z[j]) * x_i + np.sin(azi_z[j]) * y_i
            y_t = -np.sin(azi_z[j]) * x_i + np.cos(azi_z[j]) * y_i
            z_t = z_i

            x[j,i] = x_t
            y[j,i] = y_t
            z[j,i] = z_t

    traj = (x,y,z)
    pole = (pol_x,pol_y,azi_z)
    spirals = (x_b,y_b,z_b)

    print(str(proj_per_frame)+' projections per interleave')
    print(str(int(proj_per_frame/2))+' projections per spiral direction')
    print(str(total_frames*proj_per_frame)+ ' / ' + str(total_spokes) + ' spokes populated')
    print(f"Max polar tilt angle of {polar:.2f} radians")
    wraps = fmod*(np.sqrt(proj_per_frame)*0.25-0.233)
    print(f"{(2*wraps):.2f} wraps per spiral up-down")
    return traj,pole,spirals


def radial_bSSFP_3D_WASP(system_specs: cmrseq.SystemSpec,
                     samples_per_spoke: int,
                     resolution: Quantity,
                     adc_duration: Quantity,
                     flip_angle: Quantity,
                     pulse_duration: Quantity,
                     num_interleaves = int,
                     spokes_per_interleave = int,
                     dummy_shots: int = 0,
                     half_sphere=False,
                     polar_tilt=1.,
                     spiral_density=1.,
                     add_bipolar=False,
                     venc_duration = None,
                     venc_strength = None,
                     venc_direction = np.array([0.,1.,0.]),
                     m1_compensation = None, # Defines the M1 balancing at TE. Either None, "seperate" (balancing seperate from VENC) or "combined_highgrad"
                     random_seed = None
                    ):
    
    # Input handling
    if m1_compensation == "None":
        m1_compensation = None

    if venc_strength is None and venc_duration is None and add_bipolar:
        raise ValueError("Either venc_strength or venc_duration must be set to use bipolar gradients.")
    if venc_strength is None:
        venc_strength = Quantity(0., "mT/m")
    if venc_duration is None:
        venc_duration = Quantity(0., "ms")

    venc_direction = venc_direction/np.linalg.norm(venc_direction)

    if not add_bipolar and m1_compensation=="combined":
        # This is a reduntant case
        m1_compensation = "seperate"
    
    # Step 1: RF Hardpulses
    rf_block = cmrseq.bausteine.HardRFPulse(system_specs=system_specs, flip_angle=flip_angle,
                                            duration=pulse_duration,
                                            delay=Quantity(0.,'ms'),name="rf_excitation")
    
    rf_seq = cmrseq.Sequence([rf_block],system_specs=system_specs)
    
    # FA/2 RF hardpulse
    rf_block2 = cmrseq.bausteine.HardRFPulse(system_specs=system_specs, flip_angle=flip_angle/2,
                                             duration=pulse_duration,
                                             delay=Quantity(0.,'ms'),name="rf_catalyst")
    
    rf_seq2 = cmrseq.Sequence([rf_block2],system_specs=system_specs)
    

    # Step 2: Simple case for non-merged bipolars
    # Bipolar gradients, only if they are needed and not merged with M1 compensation

    bipolar = None
    bipolar_rewind = None
    if add_bipolar and m1_compensation != "combined":

        if venc_duration>0 and venc_strength==0:
            # Add delay only
            bipolar = cmrseq.bausteine.Delay(system_specs=system_specs, duration=venc_duration,
                                             name="velocity_encode_delay")
            bipolar = cmrseq.Sequence([bipolar],system_specs=system_specs)
            bipolar_rewind = cmrseq.bausteine.Delay(system_specs=system_specs, duration=venc_duration,
                                                    name="velocity_encode_rewinder_delay")
            bipolar_rewind = cmrseq.Sequence([bipolar_rewind],system_specs=system_specs)
        elif venc_strength>0:
            # Create bipolars
            bipolar = cmrseq.parametric_definitions.velocity.bipolar(system_specs=system_specs,
                                                                    venc=venc_strength,
                                                                    duration = venc_duration,
                                                                    direction=venc_direction)
            
            bipolar_rewind = cmrseq.parametric_definitions.velocity.bipolar(system_specs=system_specs,
                                                                            venc=venc_strength,
                                                                            duration = venc_duration,
                                                                            direction=-venc_direction)
    
    # Step 3: Generate 3D radial spokes
    kr_max = 1 / (2 * resolution)

    # Generate WASP spoke angles
    total_spokes = num_interleaves*spokes_per_interleave       
    rangefactor = 2 if half_sphere else 1
    traj,_,_ = gen_WASP(total_spokes,num_interleaves, polar_tilt,
                        spiral_density, rangefactor=rangefactor, random_seed=random_seed)
    # Flatten and stack to N,3
    traj = np.stack([dir.flatten() for dir in traj],axis=1)

    # Generate actual readout blocks
    ro_blocks = cmrseq.parametric_definitions.readout.radial_3D(system_specs=system_specs,
                                                                spoke_directions=traj,
                                                                samples_per_spoke=samples_per_spoke,
                                                                kr_max=kr_max,
                                                                adc_duration=adc_duration,
                                                                balanced=True)
    
    # Step 4: If compensated, re-calculate prephaser timings
    if m1_compensation == "seperate" or "combined":

        # Get M1 and M0 of just readout gradient up to echo time
        # We only care about the magnitude
        ro = deepcopy(ro_blocks[0])
        ro.remove_block('radial_prephaser_0')
        ro.remove_block('radial_prephaser_balance_0')
        ro.shift_in_time(-ro.start_time)
        echo_time = ro['adc_0'].adc_center
        readout_M1 = Quantity(np.linalg.norm(ro.calculate_moment(1,end_time=echo_time).m_as('mT/m*ms**2')),'mT/m*ms**2')
        readout_M0 = Quantity(np.linalg.norm(ro.calculate_moment(0,end_time=echo_time).m_as('mT/m*ms')),'mT/m*ms')

        desired_M1 = Quantity(0.,'mT/m*ms**2')
        if m1_compensation == "combined" and venc_strength > 0:
            # In this case, the compensation should account for the need to add the velocity encoding M1
            desired_M1 = Quantity(np.pi,'rad')/system_specs.gamma_rad/venc_strength


        # Calculate the prephaser timings
         # The worst case scenario is when the desired M1 is negative (encoding opposite to readout)
        T1, T2, d1, d2 = _optimize_prephaser_timing(system_specs=system_specs,
                                                    readout_M1=readout_M1,
                                                    readout_M0=readout_M0,
                                                    desired_M1=-desired_M1)
    # Step4b: Calculate the desired M1 for MPS
    if m1_compensation == "combined" and venc_strength > 0:
        desired_M1_MPS = desired_M1 * venc_direction
    else:
        desired_M1_MPS = Quantity(np.array([0.,0.,0.]),'mT/m*ms**2')



    # Step 5: Assemble sequence
    seq_list = []
    for ro_idx, ro_b in enumerate(ro_blocks):
        # Start with RF pulse
        seq = deepcopy(rf_seq)

        # Adjust RF and phase
        seq['rf_excitation_0'].phase_offset = Quantity(np.mod(ro_idx,2)*np.pi,'rad')
        ro_b['adc_0'].phase_offset = Quantity(np.mod(ro_idx,2)*np.pi,'rad')

        # Add standalone bipolar if needed
        if add_bipolar and m1_compensation != "combined":
            # the the first bipolar
            seq.append(bipolar, copy=True)
        
        # If compensating, need to create the new pre phasers and rewinders, per direction
        cur_readout_dir = traj[ro_idx]
        cur_readout_dir = cur_readout_dir/np.linalg.norm(cur_readout_dir)
        if m1_compensation == "seperate" or m1_compensation == "combined":
            p1_MPS = []
            p2_MPS = []
            for i in range(3):
                # First we need to find the component of the readout along the given direction
                cur_readout_M1 = cur_readout_dir[i]*readout_M1
                cur_readout_M0 = cur_readout_dir[i]*readout_M0
                G1,G2 = _calculate_optimized_prephasers(system_specs=system_specs,
                                                        readout_M1 = cur_readout_M1,
                                                        readout_M0 = cur_readout_M0,
                                                        desired_M1 = desired_M1_MPS[i],
                                                        T1=T1, T2=T2, d1=d1, d2=d2)
                p1_MPS.append(G1.m_as('mT/m'))
                p2_MPS.append(G2.m_as('mT/m'))
            p1_MPS = np.array(p1_MPS)
            p2_MPS = np.array(p2_MPS)
            
            # Create and append the prephasers
            p1_mag = np.linalg.norm(p1_MPS)
            p2_mag = np.linalg.norm(p2_MPS)
            if p1_mag>0:
                p1_dir = p1_MPS/p1_mag
                prephaser_1 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                                   orientation=p1_dir,
                                                                   amplitude=Quantity(p1_mag,'mT/m'),
                                                                   flat_duration=T1,
                                                                   rise_time=d1,
                                                                   name='radial_prephaser_comp1')
            else:
                # need to add a delay
                prephaser_1 = cmrseq.bausteine.Delay(system_specs=system_specs,
                                                    duration=T1 + 2*d1,
                                                    name='radial_prephaser_comp1')
            seq.append(prephaser_1)
                
            if p2_mag>0:
                p2_dir = p2_MPS/p2_mag
                prephaser_2 = cmrseq.bausteine.TrapezoidalGradient(system_specs=system_specs,
                                                                   orientation=p2_dir,
                                                                   amplitude=Quantity(p2_mag,'mT/m'),
                                                                   flat_duration=T2,
                                                                   rise_time=d2,
                                                                   name='radial_prephaser_comp2')
            else:
                # need to add a delay
                prephaser_1 = cmrseq.bausteine.Delay(system_specs=system_specs,
                                                    duration=T2 + 2*d2,
                                                    name='radial_prephaser_comp2')
            seq.append(prephaser_2)

            # Add the readout (remove prephaser/rewinders first)
            ro_b.remove_block('radial_prephaser_0')
            ro_b.remove_block('radial_prephaser_balance_0')
            ro_b.shift_in_time(-ro_b.start_time)
            seq.append(ro_b)
            
            # Add the rewinders
            if p2_mag>0:
                rewinder_2 = deepcopy(prephaser_2)
                rewinder_2.name = 'radial_rewinder_comp2'
                seq.append(rewinder_2)

            if p1_mag>0:
                rewinder_1 = deepcopy(prephaser_1)
                rewinder_1.name = 'radial_rewinder_comp1'
                seq.append(rewinder_1)

        else:
            # No compensation, we simply add the readout as is
            seq.append(ro_b)

        
        if add_bipolar and m1_compensation != "combined":
            # the the bipolar rewinder
            seq.append(bipolar_rewind, copy=True)
        seq_list.append(seq)

    # Set up dummy shots
    dummy_ref = deepcopy(seq_list[0])
    dummy_ref.remove_block('adc_0')
    for i in range(dummy_shots):
        cur_dummy = deepcopy(dummy_ref)
        cur_dummy['rf_excitation_0'].phase_offset = Quantity(np.mod(i+1,2)*np.pi,'rad')
        seq_list.insert(0, cur_dummy)
    
    # Add catalyst
    delay_dur = dummy_ref.duration/2 - rf_seq2.duration/2 - rf_seq.duration/2
    catalyst_delay = cmrseq.bausteine.Delay(system_specs=system_specs,
                                            duration=delay_dur,
                                            name="catalyst_delay")
    rf_seq2.append(catalyst_delay)
    rf_seq2['rf_catalyst_0'].phase_offset = Quantity(np.pi * np.mod(dummy_shots+1,2),'rad')
    seq_list.insert(0, rf_seq2)

    return seq_list




def _optimize_prephaser_timing(system_specs: cmrseq.SystemSpec, readout_M1, readout_M0, desired_M1):

    # Solve for 2 prephaser gradients to achieve desired M1 and M0 compensation

    # Everything based off the following equations
    #     _______  __G1                 ________
    #   /|       |\                    /   M1r  |
    #  / |       | \                  /    M0r  |
    # |d1|  T1   |d1|d2|    T2    |d2|
    #                \ |          | /  
    #            G2__ \|__________|/

    # desired_M1 = M0r*(T1 + T2 + 2*d1 + 2*d2) + 
    #              G1*(T1**2/2 + 1.5*T1*d1 + d1**2) + 
    #              G2*(T2**2/2 + 1.5*T2*d2 + d2**2 + (T1 + 2*d1)*(T2 + d2))+
    #              M1r
    # 
    # M0 balancing 
    # M0 = M0r + G1*(T1 + d1) + G2*(T2 + d2) = 0

    Gmax = system_specs.max_grad.m_as("mT/m")
    maxSlew = system_specs.max_slew.m_as("mT/m/ms")

    M1r = readout_M1.m_as("mT/m*ms**2")
    M0r = readout_M0.m_as("mT/m*ms")
    M1d = desired_M1.m_as("mT/m*ms**2")

    # Case A: Solve for case where G1 = Gmax, G2 = -Gmax (trapezoidal gradients)
    # Substitution: Enforce M0 = 0, max slew rate
    # T2 = -(G1*(T1+d1)+M0r)/G2-d2
    # d1 = G1/maxSlew
    # d2 = G2/maxSlew
    # G1 = Gmax
    # G2 = -Gmax
    # We can solve resulting quadratic equation for T1
    # Roots are 
    # -2*Gmax**2

    a = -Gmax
    b = -3*Gmax**2/maxSlew
    c = -2*Gmax**3/maxSlew**2 + Gmax*M0r/(2*maxSlew) + M1r - M1d +M0r**2/(2*Gmax)

    # Look for smallest real positive root
    roots = np.roots([a,b,c])
    valid_roots = roots[np.isreal(roots)]
    valid_roots = valid_roots[valid_roots>0]
    if len(valid_roots)>0:
        # Solution is valid
        # calculate the remaining parameters
        T1 = np.min(valid_roots)
        d1 = Gmax/maxSlew
        d2 = Gmax/maxSlew
        G2 = -Gmax
        G1 = Gmax
        T2 = -(G1*(T1+d1)+M0r)/G2-d2

    else:
        # Case B: Solve for case where G1<Gmax (trianglular) and G2=-Gmax (trapezoidal)
        # T2 = -(G1*d1+M0r)/G2-d2
        # T1 = 0
        # d1 = G1/maxSlew
        # d2 = G2/maxSlew
        # G2 = -Gmax
        # This results in a cubic equation, solving for G1

        a = -1/(2*Gmax*maxSlew**2)
        b = -1/maxSlew**2
        c = -Gmax/(2*maxSlew**2)
        d = 0 
        e = Gmax*M0r/(2*maxSlew) + M1r - M1d + M0r**2/(2*Gmax)
        
        roots = np.roots([a,b,c,d,e])
        # We want to largest, real root that is less that Gmax
        valid_roots = roots[np.isreal(roots)]
        valid_roots = valid_roots[valid_roots>0]
        valid_roots = valid_roots[valid_roots<=Gmax]
        if len(valid_roots)>0:
            G1 = np.max(valid_roots)
            # Calculate the remaining parameters
            d1 = G1/maxSlew
            d2 = Gmax/maxSlew
            G2 = -Gmax
            T1 = 0
            T2 = -(G1*d1+M0r)/G2-d2

        else:
            # Case C: Solve for case where G1<Gmax (triangular) and G2<Gmax (triangular)
            # We have to pre-solve the M0 solution
            # M0 = M0r + G1*d1 + G2*d2 = 0
            # d1 = G1/maxSlew
            # d2 = G2/maxSlew
            # We assume G1>0, and G2<0
            # M0 = M0r + G1**2/maxSlew - G2**2/maxSlew = 0
            # G2 = 
            # T1 = 0
            # T2 = 0
            # d1 = G1/maxSlew
            # d2 = G2/maxSlew
            # This results in a cubic equation, solving for G1
            #a = 
            raise NotImplementedError("Case C not implemented yet")
            
    # All timings must be rounded up to raster
    d1 = system_specs.time_to_raster(Quantity(d1,'ms'),raster='grad')
    d2 = system_specs.time_to_raster(Quantity(d2,'ms'),raster='grad')
    T1 = system_specs.time_to_raster(Quantity(T1,'ms'),raster='grad')
    T2 = system_specs.time_to_raster(Quantity(T2,'ms'),raster='grad')

    return T1,T2,d1,d2


def _calculate_optimized_prephasers(system_specs: cmrseq.SystemSpec, readout_M1, readout_M0, desired_M1, T1, T2, d1, d2):
    # Calculate the scaled prephasers with pre-defined timings

    # We can start with the same equations as in the optimization, but this time most parameters are known

    # desired_M1 = M0r*(T1 + T2 + 2*d1 + 2*d2) + 
    #              G1*(T1**2/2 + 1.5*T1*d1 + d1**2) + 
    #              G2*(T2**2/2 + 1.5*T2*d2 + d2**2 + (T1 + 2*d1)*(T2 + d2))+
    #              M1r
    # 
    # M0 balancing 
    # M0 = M0r + G1*(T1 + d1) + G2*(T2 + d2) = 0

    # We only need to solve for G1 and G2

    # G2 = -(M0r + G1*(T1 + d1))/(T2 + d2)

    # To simplify we use the following change of variables
    # desired_M1 = A + G1*B + G2*C
    # G2 = D + G1*E
    # desired_M1 = A + C*D + G1*(B + C*E)
    # G1 = (desired_M1 - A - C*D) / (B + C*E)

    A = readout_M0*(T1+T2 + 2*(d1+d2)) + readout_M1
    B = T1**2/2 + 1.5*T1*d1 + d1**2
    C = T2**2/2 + 1.5*T2*d2 + d2**2 + (T1 + 2*d1)*(T2 + d2)
    D = -readout_M0/(T2+d2)
    E = -(T1+d1)/(T2+d2)

    G1 = (desired_M1 - A - C*D) / (B + C*E)

    G2 = D + G1*E

    return G1, G2



    






