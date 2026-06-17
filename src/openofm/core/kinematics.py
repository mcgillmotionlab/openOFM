import numpy as np

from .linear_algebra import makeunit, angle
from .utils import addchannelsgs, getDir


def kinematics(data: dict, r: dict, jnt: list, version: str) -> dict:
    """Compute Oxford Foot Model joint kinematics.

    Parameters
    ----------
    data : dict
        Trial data dictionary, updated in-place with computed angle channels.
    r : dict
        Segment reference frame dictionary produced by :func:`~openofm.OFM.segments.segments`.
    jnt : list
        Joint definition list produced by :func:`~openofm.OFM.segments.segments`.
    version : str
        openOFM model version.

    Returns
    -------
    dict
        Updated *data* dictionary with kinematic angle channels appended.
    """
    KIN = grood_suntay(r, jnt, version)
    # update reference system
    data, _ = refsystem(data, KIN, version)
    return data

def grood_suntay(r: dict, jnt: list, version: str) -> dict:
    """Compute Grood-Suntay joint angles for all joints.

    Merged implementation that selects the correct convention based on
    *version*.  Replaces the separate ``grood_suntay_1_0`` and
    ``grood_suntay`` functions from the MATLAB toolbox.

    Parameters
    ----------
    r : dict
        Segment reference frame dictionary.
    jnt : list
        Joint definition list.  Each entry is a 3-element list
        ``[joint_name, proximal_segment, distal_segment]``.
    version : str
        openOFM model version.

    Returns
    -------
    dict
        Kinematic results keyed by joint name.
    """
    KIN = {}
    for i in range(len(jnt)):
        jnt_name = jnt[i]
        pbone = jnt_name[1]
        dbone = jnt_name[2]

        pax = r[pbone]['ort']
        dax = r[dbone]['ort']

        if pbone.startswith('Right'):
            prox_bone = pbone[5:]
        elif pbone.startswith('Left'):
            prox_bone = pbone[4:]
        else:
            prox_bone = pbone

        flx_i, abd_i, tw_i = None, None, None
        flx_j, abd_j, tw_j = None, None, None
        alpha, beta, gamma = None, None, None

        if version == "1.0":
            if prox_bone == 'Global':
                floatax, _, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax(pax, dax, mode='1.1')
                flx_i = angle(dist_z, prox_x)
                abd_i = angle(prox_y, dist_z)
                tw_i = angle(dist_x, prox_y)
                flx_j = angle(prox_y, dist_z)
                abd_j = angle(dist_z, prox_x)
                tw_j = angle(dist_x, prox_x)
            
            elif prox_bone == 'TibiaOFM':
                floatax, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax(pax, dax, mode='1.0')
                alpha = -angle(floatax, prox_x)
                beta = angle(prox_y, dist_z)
                gamma = angle(floatax, dist_y)
            
            else:
                floatax, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax(pax, dax, mode='1.0')
                alpha = -angle(floatax, prox_z)
                beta = angle(prox_y, dist_z)
                gamma = angle(floatax, dist_y)

            KIN[jnt_name[0]] = dict
            if prox_bone == 'Global':
                KIN[jnt_name[0]] = {'flx_i': flx_i, 'abd_i': abd_i, 'tw_i': tw_i,
                                  'flx_j': flx_j, 'abd_j': abd_j, 'tw_j': tw_j}
            elif prox_bone == 'TibiaOFM':
                KIN[jnt_name[0]] = {'flx': alpha, 'abd': gamma, 'tw': beta}
            else:
                KIN[jnt_name[0]] = {'flx': alpha, 'abd': beta, 'tw': gamma}

        elif version == "1.1":
            floatax, _, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z = makeax(pax, dax, mode='1.1')

            if prox_bone == 'Global':
                flx_i = angle(dist_y, prox_x)
                abd_i = angle(prox_y, dist_y)
                tw_i = angle(dist_x, prox_y)
                flx_j = angle(prox_y, dist_y)
                abd_j = angle(dist_y, prox_x)
                tw_j = angle(dist_x, prox_x)

            if prox_bone == 'ForeFoot':
                alpha = angle(floatax, prox_y)
                beta = -angle(prox_z, dist_x)
                gamma = angle(floatax, dist_z)
            else:
                alpha = angle(floatax, prox_x)
                beta = - angle(prox_z, dist_x)
                gamma = angle(floatax, dist_z)

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


def makeax(pax: list, dax: list, mode: str = '1.1') -> tuple:
    """Gather and normalise proximal/distal axes for Grood-Suntay computation.

    Parameters
    ----------
    pax : list
        Per-frame proximal segment axes; each element is a ``(3, 3)`` array.
    dax : list
        Per-frame distal segment axes; each element is a ``(3, 3)`` array.
    mode : str, optional
        Axis convention.  ``'1.1'`` (default) or ``'1.0'`` (legacy).

    Returns
    -------
    tuple
        ``(floatax, [floatax_isb,] prox_x, dist_x, prox_y, dist_y, prox_z, dist_z)``
        as ``(N, 3)`` unit-vector arrays.  ``floatax_isb`` is only included
        when *mode* is ``'1.1'``.
    """
    num_frames = len(pax)
    num_axes = 3

    prox_x = np.zeros((num_frames, num_axes))
    prox_y = np.zeros((num_frames, num_axes))
    prox_z = np.zeros((num_frames, num_axes))

    dist_x = np.zeros((num_frames, num_axes))
    dist_y = np.zeros((num_frames, num_axes))
    dist_z = np.zeros((num_frames, num_axes))

    floatax = np.zeros((num_frames, num_axes))
    
    if mode == '1.1':
        floatax_isb = np.zeros((num_frames, num_axes))
    elif mode != '1.0':
        raise ValueError(f"Unknown mode for make_axes_merged: {mode}")

    for i in range(num_frames):
        prox_x[i, :] = makeunit(pax[i][0, :])
        prox_y[i, :] = makeunit(pax[i][1, :])
        prox_z[i, :] = makeunit(pax[i][2, :])

        dist_x[i, :] = makeunit(dax[i][0, :])
        dist_y[i, :] = makeunit(dax[i][1, :])
        dist_z[i, :] = makeunit(dax[i][2, :])

        if mode == '1.1':
            floatax[i, :] = np.cross(dist_x[i, :], prox_z[i, :])
            floatax_isb[i, :] = np.cross(dist_y[i, :], prox_z[i, :])
        else: # mode == '1.0'
            floatax[i, :] = np.cross(dist_z[i, :], prox_y[i, :])

    floatax = makeunit(floatax)
    prox_x = makeunit(prox_x)
    dist_x = makeunit(dist_x)
    prox_y = makeunit(prox_y)
    dist_y = makeunit(dist_y)
    prox_z = makeunit(prox_z)
    dist_z = makeunit(dist_z)

    if mode == '1.1':
        floatax_isb = makeunit(floatax_isb)
        return floatax, floatax_isb, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z
    else: # mode == '1.0'
        return floatax, prox_x, dist_x, prox_y, dist_y, prox_z, dist_z

def refsystem(data: dict, KIN: dict, version: str) -> tuple[dict, dict]:
    """Apply direction-dependent sign corrections to match the Oxford Foot Model convention.

    Parameters
    ----------
    data : dict
        Trial data dictionary.
    KIN : dict
        Raw Grood-Suntay angles keyed by joint name.
    version : str
        openOFM model version.

    Returns
    -------
    data : dict
        Updated trial data dictionary with angle channels appended.
    KIN : dict
        Sign-corrected kinematic dictionary.
    """
    direction = getDir(data)

    # Define direction mapping for tibia angles
    dir_map = {
        'Ipos': {
            'RightTibiaLab': {'flx': ('flx_i', 1), 'abd': ('abd_i', -1), 'tw': ('tw_i', 1)},
            'LeftTibiaLab':  {'flx': ('flx_i', 1), 'abd': ('abd_i', 1),  'tw': ('tw_i', -1)},
        },
        'Ineg': {
            'RightTibiaLab': {'flx': ('flx_i', -1), 'abd': ('abd_i', 1),  'tw': ('tw_i', -1)},
            'LeftTibiaLab':  {'flx': ('flx_i', -1), 'abd': ('abd_i', -1), 'tw': ('tw_i', 1)},
        },
        'Jpos': {
            'RightTibiaLab': {'flx': ('flx_j', 1),  'abd': ('abd_j', 1),  'tw': ('tw_j', -1)},
            'LeftTibiaLab':  {'flx': ('flx_j', 1),  'abd': ('abd_j', -1), 'tw': ('tw_j', 1)},
        },
        'Jneg': {
            'RightTibiaLab': {'flx': ('flx_j', -1), 'abd': ('abd_j', -1), 'tw': ('tw_j', 1)},
            'LeftTibiaLab':  {'flx': ('flx_j', -1), 'abd': ('abd_j', 1),  'tw': ('tw_j', -1)},
        }
    }

    # Apply direction transformation if applicable
    if direction in dir_map:
        for segment, angles in dir_map[direction].items():
            for angle, (src, sign) in angles.items():
                KIN[segment][angle] = sign * KIN[segment][src]

    # Handle version-based modifications
    if version in ('1.0', '1.1'):
        left_segments = ['LeftAnkleOFM', 'LeftFFTBA', 'LeftMidFoot']
        for seg in left_segments:
            KIN[seg]['abd'] *= -1
            KIN[seg]['tw'] *= -1

        # Version-specific parts
        if version == '1.0':
            KIN['LeftMTP']['abd'] *= -1
            KIN['LeftMTP']['tw'] *= -1
        elif version == '1.1':
            KIN['RightMTP']['abd'] *= -1

    # ADD COMPUTED ANGLES TO DATA STRUCT
    data = addchannelsgs(data, KIN)
    return data, KIN