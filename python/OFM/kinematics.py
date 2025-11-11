import numpy as np
from linear_algebra.linear_algebra import makeunit, angle
from utils.utils import addchannelsgs, getDir


def kinematics(data, r, jnt, version):
    """ wrapper function to access different computations"""
    KIN = grood_suntay(r, jnt, version)
    # update reference system
    data, _ = refsystem(data, KIN, version)
    return data

def grood_suntay(r, jnt, version):
    """
    Merged version of grood_suntay_1_0 and grood_suntay.
    Selects the correct logic based on the 'version' string.
    """
    KIN = {}
    for i in range(len(jnt)):
        jnt_name = jnt[i]
        pbone = jnt_name[1]
        dbone = jnt_name[2]

        pax = r[pbone]['ort']  # stores xyz local axes for each frame
        dax = r[dbone]['ort']

        # Standardize variable name to 'prox_bone'
        if pbone.startswith('Right'):
            prox_bone = pbone[5:]
        elif pbone.startswith('Left'):
            prox_bone = pbone[4:]
        else:
            prox_bone = pbone
        
        # Initialize all potential angle variables
        flx_i, abd_i, tw_i = None, None, None
        flx_j, abd_j, tw_j = None, None, None
        alpha, beta, gamma = None, None, None

        if version == "1.0":
            if prox_bone == 'Global':
                floatax, _, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax(pax, dax)
                # v1.0 Global calculations
                flx_i = angle(dist_z, prox_x)
                abd_i = angle(prox_y, dist_z)
                tw_i = angle(dist_x, prox_y)
                flx_j = angle(prox_y, dist_z)
                abd_j = angle(dist_z, prox_x)
                tw_j = angle(dist_x, prox_x)
            
            elif prox_bone == 'TibiaOFM':
                floatax, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax_1_0(pax, dax)
                # v1.0 TibiaOFM calculations
                alpha = -angle(floatax, prox_x)
                beta = angle(prox_y, dist_z)
                gamma = angle(floatax, dist_y)
            
            else:
                floatax, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax_1_0(pax, dax)
                # v1.0 Else calculations
                alpha = -angle(floatax, prox_z)
                beta = angle(prox_y, dist_z)
                gamma = angle(floatax, dist_y)

            # v1.0 KIN Assignment
            KIN[jnt_name[0]] = dict
            if prox_bone == 'Global':
                KIN[jnt_name[0]] = {'flx_i': flx_i, 'abd_i': abd_i, 'tw_i': tw_i,
                                  'flx_j': flx_j, 'abd_j': abd_j, 'tw_j': tw_j}
            elif prox_bone == 'TibiaOFM':
                KIN[jnt_name[0]] = {'flx': alpha, 'abd': gamma, 'tw': beta}
            else:
                KIN[jnt_name[0]] = {'flx': alpha, 'abd': beta, 'tw': gamma}

        elif version == "1.1":
            # Version 1.1 LOGIC
            # v1.1 calls makeax once at the top
            floatax, _, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax(pax, dax)

            if prox_bone == 'Global':
                # v1.1 Global calculations
                flx_i = angle(dist_y, prox_x)
                abd_i = angle(prox_y, dist_y)
                tw_i = angle(dist_x, prox_y)
                flx_j = angle(prox_y, dist_y)
                abd_j = angle(dist_y, prox_x)
                tw_j = angle(dist_x, prox_x)

            # v1.1 non-Global calculations
            if prox_bone == 'ForeFoot':
                alpha = angle(floatax, prox_y)
                beta = -angle(prox_z, dist_x)
                gamma = angle(floatax, dist_z)
            else:
                alpha = angle(floatax, prox_x)
                beta = - angle(prox_z, dist_x)
                gamma = angle(floatax, dist_z)

            # v1.1 KIN Assignment
            KIN[jnt_name[0]] = dict
            if prox_bone == 'Global':
                KIN[jnt_name[0]] = {'flx_i': flx_i, 'abd_i': abd_i, 'tw_i': tw_i,
                                  'flx_j': flx_j, 'abd_j': abd_j, 'tw_j': tw_j}
            elif prox_bone == 'HindFoot':
                KIN[jnt_name[0]] = {'flx': alpha, 'abd': beta, 'tw': gamma}
            else:
                KIN[jnt_name[0]] = {'flx': alpha, 'abd': gamma, 'tw': beta}
        
        else:
            raise ValueError(f"Unknown kinematics version: {version}")

    return KIN


def makeax_1_0(pax, dax):
    """ helper function to gather axes for grood and suntay"""
    num_frames = len(pax)
    num_axes = 3

    prox_x = np.zeros((num_frames, num_axes))
    prox_y = np.zeros((num_frames, num_axes))
    prox_z = np.zeros((num_frames, num_axes))

    dist_x = np.zeros((num_frames, num_axes))
    dist_y = np.zeros((num_frames, num_axes))
    dist_z = np.zeros((num_frames, num_axes))

    floatax = np.zeros((num_frames, num_axes))

    for i in range(num_frames):
        prox_x[i, :] = makeunit(pax[i][0, :])
        prox_y[i, :] = makeunit(pax[i][1, :])
        prox_z[i, :] = makeunit(pax[i][2, :])

        dist_x[i, :] = makeunit(dax[i][0, :])
        dist_y[i, :] = makeunit(dax[i][1, :])
        dist_z[i, :] = makeunit(dax[i][2, :])

        floatax[i, :] = np.cross(dist_z[i, :], prox_y[i, :])

    floatax = makeunit(floatax)
    prox_x = makeunit(prox_x)
    dist_x = makeunit(dist_x)
    prox_y = makeunit(prox_y)
    dist_y = makeunit(dist_y)
    prox_z = makeunit(prox_z)
    dist_z = makeunit(dist_z)

    return floatax, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z


def makeax(pax, dax):
    """ helper function to gather axes for grood and suntay"""
    num_frames = len(pax)
    num_axes = 3

    prox_x = np.zeros((num_frames, num_axes))
    prox_y = np.zeros((num_frames, num_axes))
    prox_z = np.zeros((num_frames, num_axes))

    dist_x = np.zeros((num_frames, num_axes))
    dist_y = np.zeros((num_frames, num_axes))
    dist_z = np.zeros((num_frames, num_axes))

    floatax = np.zeros((num_frames, num_axes))
    floatax_isb = np.zeros((num_frames, num_axes))

    for i in range(num_frames):
        prox_x[i, :] = makeunit(pax[i][0, :])
        prox_y[i, :] = makeunit(pax[i][1, :])
        prox_z[i, :] = makeunit(pax[i][2, :])

        dist_x[i, :] = makeunit(dax[i][0, :])
        dist_y[i, :] = makeunit(dax[i][1, :])
        dist_z[i, :] = makeunit(dax[i][2, :])

        floatax[i, :] = np.cross(dist_x[i, :], prox_z[i, :])
        floatax_isb[i, :] = np.cross(dist_y[i, :], prox_z[i, :])

    floatax = makeunit(floatax)
    floatax_isb = makeunit(floatax_isb)

    prox_x = makeunit(prox_x)
    dist_x = makeunit(dist_x)
    prox_y = makeunit(prox_y)
    dist_y = makeunit(dist_y)
    prox_z = makeunit(prox_z)
    dist_z = makeunit(dist_z)

    return floatax, floatax_isb, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z


def refsystem(data, KIN, version):
    """ update reference system to match oxford food model"""

    direction = getDir(data)

    if direction == 'Ipos':
        # todo : test this direction
        KIN['RightTibiaLab']['flx'] = KIN['RightTibiaLab']['flx_i']
        KIN['RightTibiaLab']['abd'] = - KIN['RightTibiaLab']['abd_i']
        KIN['RightTibiaLab']['tw'] = KIN['RightTibiaLab']['tw_i']

        KIN['LeftTibiaLab']['flx'] = KIN['LeftTibiaLab']['flx_i']
        KIN['LeftTibiaLab']['abd'] = KIN['LeftTibiaLab']['abd_i']
        KIN['LeftTibiaLab']['tw'] = -KIN['LeftTibiaLab']['tw_i']

    elif direction == 'Ineg':
        KIN['RightTibiaLab']['flx'] = -KIN['RightTibiaLab']['flx_i']
        KIN['RightTibiaLab']['abd'] = KIN['RightTibiaLab']['abd_i']
        KIN['RightTibiaLab']['tw'] = -KIN['RightTibiaLab']['tw_i']

        KIN['LeftTibiaLab']['flx'] = -KIN['LeftTibiaLab']['flx_i']
        KIN['LeftTibiaLab']['abd'] = -KIN['LeftTibiaLab']['abd_i']
        KIN['LeftTibiaLab']['tw'] = KIN['LeftTibiaLab']['tw_i']

    elif direction == 'Jpos':
        KIN['RightTibiaLab']['flx'] = KIN['RightTibiaLab']['flx_j']
        KIN['RightTibiaLab']['abd'] = KIN['RightTibiaLab']['abd_j']
        KIN['RightTibiaLab']['tw'] = - KIN['RightTibiaLab']['tw_j']

        KIN['LeftTibiaLab']['flx'] = KIN['LeftTibiaLab']['flx_j']
        KIN['LeftTibiaLab']['abd'] = - KIN['LeftTibiaLab']['abd_j']
        KIN['LeftTibiaLab']['tw'] = KIN['LeftTibiaLab']['tw_j']

    elif direction == 'Jneg':
        KIN['RightTibiaLab']['flx'] = -KIN['RightTibiaLab']['flx_j']
        KIN['RightTibiaLab']['abd'] = - KIN['RightTibiaLab']['abd_j']
        KIN['RightTibiaLab']['tw'] = KIN['RightTibiaLab']['tw_j']

        KIN['LeftTibiaLab']['flx'] = - KIN['LeftTibiaLab']['flx_j']
        KIN['LeftTibiaLab']['abd'] = KIN['LeftTibiaLab']['abd_j']
        KIN['LeftTibiaLab']['tw'] = - KIN['LeftTibiaLab']['tw_j']

    if version == '1.0':
        KIN['LeftAnkleOFM']['abd'] = - KIN['LeftAnkleOFM']['abd']
        KIN['LeftAnkleOFM']['tw'] = - KIN['LeftAnkleOFM']['tw']

        KIN['LeftFFTBA']['abd'] = -KIN['LeftFFTBA']['abd']
        KIN['LeftFFTBA']['tw'] = -KIN['LeftFFTBA']['tw']

        KIN['LeftMidFoot']['abd'] = -KIN['LeftMidFoot']['abd']
        KIN['LeftMidFoot']['tw'] = -KIN['LeftMidFoot']['tw']

        KIN['LeftMTP']['abd'] = -KIN['LeftMTP']['abd']
        KIN['LeftMTP']['tw'] = -KIN['LeftMTP']['tw']

    elif version == '1.1':
        KIN['LeftAnkleOFM']['abd'] = -KIN['LeftAnkleOFM']['abd']
        KIN['LeftAnkleOFM']['tw'] = -KIN['LeftAnkleOFM']['tw']

        KIN['LeftFFTBA']['abd'] = -KIN['LeftFFTBA']['abd']
        KIN['LeftFFTBA']['tw'] = -KIN['LeftFFTBA']['tw']

        KIN['LeftMidFoot']['abd'] = -KIN['LeftMidFoot']['abd']
        KIN['LeftMidFoot']['tw'] = -KIN['LeftMidFoot']['tw']

        KIN['RightMTP']['abd'] = -KIN['RightMTP']['abd']

    # ----4 : ADD COMPUTED ANGLES TO DATA STRUCT------------------------------------
    data = addchannelsgs(data, KIN)

    return data, KIN