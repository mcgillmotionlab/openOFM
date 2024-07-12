import numpy as np
from linear_algebra.linear_algebra import makeunit, gunit, ctransform, create_lcs, rotate_axes, magnitude


def hipjointcentrePiG_data(data=None):
    """
    data = HIPJOINTCENTREPIG_DATA(data,test) computes left and right hip joint
    centers for plug-in gait (PiG) marker data
    ARGUMENTS
      data      ... dict, containing PiG markers. Required markers are
                    'RASI','LASI','SACR' or 'RASI','LASI','RPSI','LPSI'
    RETURNS
      data      ... dict, with appended hip joint center virtual marker as
                    RHipJC and LHipJC.
    NOTES
    - computation method based on Davis et al. "A gait analysis data
    collection and reduction technique". Hum Mov Sci. 1991. (see also
    PiG manual)
    """

    # set values from Davis et al. 1991
    COSBETA = np.cos(0.314)
    SINBETA = np.sin(0.314)
    COSTHETA = np.cos(0.496)
    SINTHETA = np.sin(0.496)

    # Extract pelvis marker positions
    RASI = data['RASI']
    LASI = data['LASI']

    if 'RPSI' in data:
        RPSI = data['RPSI']
        LPSI = data['LPSI']
        SACR = (RPSI + LPSI) / 2
    else:
        SACR = data['SACR']

    # Extract info from data
    mDiam = data['parameters']['PROCESSING']['MarkerDiameter']['value']
    rLegLength = data['parameters']['PROCESSING']['RLegLength']['value']
    lLegLength = data['parameters']['PROCESSING']['LLegLength']['value']
    interAsis = data['parameters']['PROCESSING']['InterAsisDistance']['value']

    # compute basic quantities
    legLength = np.mean(np.array([rLegLength, lLegLength]))
    asisTroc = (0.1288 * legLength) - 48.56

    # Define pelvis coordinate system
    PELO = (LASI + RASI) / 2                  # origin (O)
    PELy = makeunit(LASI - PELO)  # lateral (L)
    PELtemp = SACR - PELO                     # temp anterior
    PELz = makeunit(np.cross(PELy, PELtemp))  # proximal (P)
    PELx = makeunit(np.cross(PELy, PELz))  # anterior (A)

    # Compute hip joint centers
    side = np.array(['R', 'L'])
    for i in np.arange(len(side)):

        # Compute hip joint center in pelvis coordinate system (PCS)
        C = (legLength * 0.115) - 15.3
        HipPCSx = C * COSTHETA * SINBETA - (asisTroc + mDiam / 2) * COSBETA
        HipPCSy = - (C * SINTHETA - (interAsis / 2))
        HipPCSz = - C * COSTHETA * COSBETA - (asisTroc + mDiam / 2) * SINBETA
        if side[i] == 'R':
            HipPCSy = - HipPCSy
        HipPCS = np.array([HipPCSx, HipPCSy, HipPCSz]).T

        # Transform from pelvis coordinate system to global coordinate system
        HipGCS = np.ones(RASI.shape)
        GCS = gunit()
        rows = RASI.shape[0]
        for j in np.arange(rows):
            PCS = np.array([PELx[j, :], PELy[j, :], PELz[j, :]])
            HipGCS[j, :] = ctransform(PCS, GCS, HipPCS) + PELO[j, :]

        # add to data dict
        data[side[i] + 'HipJC'] = HipGCS

    return data


def kneejointcenterPiG(data):

    # Compute joint offsets for knee and ankle
    KneeWidth = (data['parameters']['PROCESSING']['RKneeWidth']['value'] +
                 data['parameters']['PROCESSING']['LKneeWidth']['value'])/2
    KneeOffset = (KneeWidth + data['parameters']['PROCESSING']['MarkerDiameter']['value']) / 2

    # Repeat for right and left sides
    sides = ['R', 'L']
    for side in sides:
        # Extract some PiG markers
        KNE = data[side + 'KNE']

        # Compute knee joint centre
        # computation based on pyCGM.py's interpretation of PiG 'chord function'

        # Extract openfoot hip joint centers
        HipJC = data[side + 'HipJC']

        # Create femur segment
        # Extract marker and value for femur rotation
        THI = data[side + 'THI']
        VCMThighOffset = data['parameters']['PROCESSING'][side + 'ThighRotation']['value']

        # Calculate the femur rotation given a thigh offset
        if VCMThighOffset != 0:
            FemurRotation = np.zeros((HipJC.shape[0], 1))
            for i in range(HipJC.shape[0]):
                _, _, _, _, Taxes = create_lcs(HipJC[i, :], KNE[i, :] - HipJC[i, :], THI[i, :] - KNE[i, :], 'zxy')

                THI_lcl_Taxes = ctransform(gunit(), Taxes, THI[i, :] - HipJC[i, :])
                wy = THI_lcl_Taxes[1]
                wz = THI_lcl_Taxes[2]
                mag = np.linalg.norm(HipJC[i, :] - KNE[i, :])
                thi = np.arcsin(KneeOffset/mag)
                psi = VCMThighOffset

                a = wy * wy
                b = 2 * np.cos(psi) * np.sin(psi) * np.sin(thi) * wy * wz
                c = np.sin(psi) * np.sin(psi) * (np.sin(thi) * np.sin(thi) * wz * wz - np.cos(thi) * np.cos(thi) * wy * wy)

                thetaplus = np.arcsin((-b + np.sqrt(b * b - 4 * a * c)) / (2 * a))[0]
                thetaminus = np.arcsin((-b - np.sqrt(b * b - 4 * a * c)) / (2 * a))[0]

                if thetaplus * VCMThighOffset > 0:
                    FemurRotation[i, :] = -thetaminus
                else:
                    FemurRotation[i, :] = -thetaplus
        else:
            FemurRotation = np.zeros((HipJC.shape[0], 1))

        FemurRotation = np.mean(FemurRotation)

        # Correct thigh wand marker
        THI_lcl_Thigh = np.zeros_like(THI)
        THR = np.zeros_like(THI)
        for i in range(THI.shape[0]):
            _, _, _, _, Thigh = create_lcs(KNE[i, :], HipJC[i, :] - KNE[i, :], KNE[i, :] - THI[i, :], 'zxy')
            THI_lcl_Thigh[i, :] = ctransform(gunit(), Thigh, THI[i, :] - KNE[i, :])
            if side == 'L':
                rot_axes = rotate_axes(Thigh, np.rad2deg(-FemurRotation), 'z')
            else:
                rot_axes = rotate_axes(Thigh, np.rad2deg(FemurRotation), 'z')
            THR_vec_gbl = ctransform(rot_axes, gunit(), THI_lcl_Thigh[i, :])
            THR[i, :] = THR_vec_gbl + KNE[i, :]

        # Create knee joint center based on corrected wand marker
        KneeJC = chordPiG(THR, HipJC, KNE, KneeOffset)
        data[side + 'KneeJC'] = KneeJC

    return data


def anklejointcenterPiG(data):
    # Compute joint offsets and ankle
    AnkleWidth = (data['parameters']['PROCESSING']['RAnkleWidth']['value'] +
                  data['parameters']['PROCESSING']['LAnkleWidth']['value']) / 2
    AnkleOffset = (AnkleWidth + data['parameters']['PROCESSING']['MarkerDiameter']['value']) / 2

    # Repeat for right and left sides
    sides = ['R', 'L']
    for side in sides:
        # Create tibia segment
        # Extract values for shank offset and knee joint center
        ShankOffset = data['parameters']['PROCESSING'][side + 'ShankRotation']['value']
        KneeJC = data[side + 'KneeJC']
        TIB = data[side + 'TIB']
        ANK = data[side + 'ANK']

        # Calculate tibia rotation
        TibiaRotation = np.zeros((KneeJC.shape[0], 1))
        if ShankOffset != 0:
            for i in range(KneeJC.shape[0]):
                _, _, _, _, Taxes = create_lcs(KneeJC[i, :], ANK[i, :] - KneeJC[i, :], TIB[i, :] - ANK[i, :], 'zxy')
                TIB_lcl_Taxes = ctransform(gunit(), Taxes, TIB[i, :] - KneeJC[i, :])
                vy = TIB_lcl_Taxes[1]
                vz = TIB_lcl_Taxes[2]
                #todo: check magnitude calculation
                mag = np.linalg.norm(KneeJC[i, :] - ANK[i, :])
                thi = np.arcsin(AnkleOffset/mag)
                psi = ShankOffset

                a = vy * vy
                b = 2 * np.cos(psi) * np.sin(psi) * np.sin(thi) * vy * vz
                c = np.sin(psi) * np.sin(psi) * (np.sin(thi) * np.sin(thi) * vz * vz - np.cos(thi) * np.cos(thi) * vy * vy)

                thetaplus = np.arcsin((-b + np.sqrt(b * b - 4 * a * c)) / (2 * a))
                thetaminus = np.arcsin((-b - np.sqrt(b * b - 4 * a * c)) / (2 * a))

                if thetaplus * ShankOffset > 0:
                    TibiaRotation[i, :] = -thetaminus
                else:
                    TibiaRotation[i, :] = -thetaplus
        else:
            TibiaRotation = np.zeros((KneeJC.shape[0], 1))

        TibiaRotation = np.mean(TibiaRotation)

        # Correct TIB marker
        TIB_lcl_Shank = np.zeros_like(TIB)
        TIR = np.zeros_like(TIB)
        for i in range(KneeJC.shape[0]):
            _, _, _, _, Shank = create_lcs(ANK[i, :], KneeJC[i, :] - ANK[i, :], TIB[i, :] - ANK[i, :], 'yxz')
            TIB_lcl_Shank[i, :] = ctransform(gunit(), Shank, TIB[i, :] - ANK[i, :])
            if side == 'L':
                rot_axes = rotate_axes(Shank, np.rad2deg(-TibiaRotation), 'y')
            else:
                rot_axes = rotate_axes(Shank, np.rad2deg(TibiaRotation), 'y')
            TIR_vec_gbl = ctransform(rot_axes, gunit(), TIB_lcl_Shank[i, :])
            TIR[i, :] = TIR_vec_gbl + ANK[i, :]

        # Create ankle joint center marker
        data[side + 'TIR'] = TIR
        AnkleJC = chordPiG(TIR, KneeJC, ANK, AnkleOffset)
        data[side + 'AnkleJC'] = AnkleJC

    return data


def getbones_data(data):
    """  retrieve "bone" information from data dict and creates joints.
    Arguments
        data    ... dict. Data_Paper_Not_Shared containing required channels
    Returns
        jnt     ...
        data
        bone
    """
    bone = []
    jnt = []
    ch = data.keys()

    # Tibia relative to lab
    if 'RLabTIB0' in ch:
        chname = 'RLabTIB0'
        bplate = [chname[:7], 'RightTibiaLab']
        bone.append(bplate)

    # Tibia relative to the lab
    if 'RLabTIB0' in ch:
        jplate = ['RightTibiaLab', 'Global', 'RightTibiaLab']
        bplate = ['GLB', 'Global']
        jnt.append(jplate)
        bone.append(bplate)

    if 'RTIB0' in ch and 'RHDF0' in ch:
        chname = 'RTIB0'
        jplate = ['RightAnkleOFM', 'RightTibiaOFM', 'RightHindFoot']
        bplate = [chname[:4], 'RightTibiaOFM']
        jnt.append(jplate)
        bone.append(bplate)

    # tibia and ff
    if 'RTIB0' in ch and 'RFOF0' in ch:
        chname = 'RTIB0'
        jplate = ['RightFFTBA', 'RightTibiaOFM', 'RightForeFoot']
        bplate = [chname[:4], 'RightTibiaOFM']
        jnt.append(jplate)
        bone.append(bplate)

    if 'RHDF0' in ch and 'RFOF0' in ch:
        chname = 'RHDF0'
        jplate = ['RightMidFoot', 'RightHindFoot', 'RightForeFoot']
        bplate = [chname[:4], 'RightHindFoot']
        jnt.append(jplate)
        bone.append(bplate)

    if 'RFOF0' in ch and 'RHLX0' in ch:
        chname = 'RFOF0'
        jplate = ['RightMTP', 'RightForeFoot', 'RightHallux']
        bplate = [chname[:4], 'RightForeFoot']
        jnt.append(jplate)
        bone.append(bplate)

    if 'RHLX0' in ch:
        chname = 'RHLX0'
        bplate = [chname[:4], 'RightHallux']
        bone.append(bplate)

    if 'LTIB0' in ch and 'LHDF0' in ch:
        chname = 'LTIB0'
        jplate = ['LeftAnkleOFM', 'LeftTibiaOFM', 'LeftHindFoot']
        bplate = [chname[:4], 'LeftTibiaOFM']
        jnt.append(jplate)
        bone.append(bplate)

    # Tibia relative to lab
    if 'LLabTIB0' in ch:
        chname = 'LLabTIB0'
        jplate = ['LeftTibiaLab', 'Global', 'LeftTibiaLab']
        bplate = ['GLB', 'Global']
        jnt.append(jplate)
        bone.append(bplate)

    if 'LLabTIB0' in ch:
        chname = 'LLabTIB0'
        bplate = [chname[:7], 'LeftTibiaLab']
        bone.append(bplate)

    # tibia and ff
    if 'LTIB0' in ch and 'LFOF0' in ch:
        chname = 'LTIB0'
        jplate = ['LeftFFTBA', 'LeftTibiaOFM', 'LeftForeFoot']
        bplate = [chname[:4], 'LeftTibiaOFM']
        jnt.append(jplate)
        bone.append(bplate)

    if 'LHDF0' in ch and 'LFOF0' in ch:
        chname = 'LHDF0'
        jplate = ['LeftMidFoot', 'LeftHindFoot', 'LeftForeFoot']
        bplate = [chname[:4], 'LeftHindFoot']
        jnt.append(jplate)
        bone.append(bplate)

    if 'LFOF0' in ch and 'LHLX0' in ch:
        chname = 'LFOF0'
        jplate = ['LeftMTP', 'LeftForeFoot', 'LeftHallux']
        bplate = [chname[:4], 'LeftForeFoot']
        jnt.append(jplate)
        bone.append(bplate)

    if 'LHLX0' in ch:
        chname = 'LHLX0'
        bplate = [chname[:4], 'LeftHallux']
        bone.append(bplate)

    # reformat bones
    r = prep_bones(data, bone)

    return r, jnt, data




def chordPiG(a, b, c, delta):
    """
     jc = CHORDPIG(a,b,c,delta) computes knee and ankle joint centres according
     to the plug-in gait 'chord' function
     ARGUMENTS
       a       ...  wand marker data (n x 3 matrix)
       b       ...  proximal joint centre (n x 3 matrix)
       c       ...  distal marker (n x 3 matrix)
       delta   ... (jointWidth/2) + mDiameter/2 (double);
     RETURNS
       jc      ...  The joint centre in global coordinate system
     See also bmech_jointcentrePiG, jointcentrePiG_dat
     NOTES
     - See vicon user manual for chord function definition (see help fileS)
     - Thanks to Seungeun Yeon, Mathew Schwartz, Filipe Alves Caixeta,
       and Robert Van-wesep. See: https://github.com/cadop/pyCGM
    """
    # make the two vector using 3 markers, which is on the same plane.
    v1 = a - c
    v2 = b - c
    # v3 is cross vector of v1, v2, and then it normalized.
    v3 = makeunit(np.cross(v1, v2))
    m = (b + c) / 2
    len_ = magnitude(b-m, axis=1)
    theta = np.arccos(delta / magnitude(v2, axis=1))
    csVec = np.cos(theta * 2)
    snVec = np.sin(theta * 2)
    uxMat = v3[:, 0].reshape(((v3[:, 0]).shape[0], 1))
    uyMat = v3[:, 1].reshape(((v3[:, 1]).shape[0], 1))
    uzMat = v3[:, 2].reshape(((v3[:, 2]).shape[0], 1))
    # this rotation matrix is called Rodriques' rotation formula. In order to
    # make a plane, at least 3 number of markers is required which means three
    # physical markers on the segment can make a plane.
    # Then the orthogonal vector of the plane will be rotating axis.
    # joint center is determined by rotating the one vector of plane around
    # rotating axis.
    jc = np.zeros(a.shape)
    for i in np.arange(len(uxMat)):
        cs = csVec[i].item()
        sn = snVec[i].item()
        ux = uxMat[i, :].item()
        uy = uyMat[i, :].item()
        uz = uzMat[i, :].item()
        rot = np.array([[cs + ux ** 2 * (1 - cs), ux * uy * (1 - cs) - uz * sn, ux * uz * (1 - cs) + uy * sn],
                        [uy * ux * (1.0 - cs) + uz * sn, cs + uy ** 2 * (1 - cs), uy * uz * (1 - cs) - ux * sn],
                        [uz * ux * (1.0 - cs) - uy * sn, uz * uy * (1.0 - cs) + ux * sn, cs + uz ** 2 * (1 - cs)]])
        r = np.matmul(rot, v2[i, :].reshape((v2[i, :].shape[0], 1)))
        r *= len_[i]/(magnitude(r.T, axis=1))
        for j in np.arange(jc.shape[1]):
            jc[i, j] = r[j] + m[i, j]
    return jc


def prep_bones(data, bone, dimOFM=None):
    # 0 is origin of bone (zero)
    # x points "forward"
    # y points "up"
    # z is medial (left) or lateral (right) vector

    if dimOFM is None:
        dimOFM = ['0', '1', '2', '3']

    r = {}
    for i in range(len(bone)):
        d = [None] * len(dimOFM)

        if bone[i][0] == 'GLB':
            d[0] = np.zeros(data[bone[i + 1][0] + dimOFM[0]].shape)
            d[1] = np.column_stack((d[0][:, 0] + 10, d[0][:, 1:3]))
            d[2] = np.column_stack((d[0][:, 0], d[0][:, 1] + 10, d[0][:, 2]))
            d[3] = np.column_stack((d[0][:, 0:2], d[0][:, 2] + 10))
        else:
            for j in range(len(dimOFM)):
                d[j] = data[bone[i][0] + dimOFM[j]]

        bn = bone[i][1]
        ort = getdata(d)  # Assuming getdataOFM is defined elsewhere
        r[bn] = {'ort': ort}

    return r


def getdata(d):
    """ helper function to organize matrices"""
    #todo: check the division by 10
    x = (d[1] - d[0]) / 10  # "Forward" - Origin: Creates anterior vector
    y = (d[2] - d[0]) / 10  # "Up" - Origin: Creates medial vector (right side), Lateral vector (left side)
    z = (d[3] - d[0]) / 10  # "Side" - Origin: Creates vector along long axis of bone

    rw = x.shape[0]
    ort = []
    for i in range(rw):
        ort.append(np.vstack((x[i], y[i], z[i])))

    return ort
