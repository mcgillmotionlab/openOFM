import numpy as np
from linear_algebra.linear_algebra import create_lcs, magnitude, pointonline, point_to_plane
from PiG.pig import getbones_data


def segments(data, version):
    """
       creates segment 'bones'
      for use in kinematic / kinetic modelling. Bones are virtual markers
      representing segment axes.
     ARGUMENTS
       data         ... struct, trial data
       settings     ... struct, information to guide computational options
                        settings.test: bool (default=False), If true,
                        runs unit test settings.HJC: options PiG=chord
                        function, Harrington
     RETURNS
       data         ... Zoo data with new 'bones' appended

     NOTES
     - Following anthropometric/metainfo data must be available:
       'MarkerDiameter, R/LLegLength,R/LKneeWidth,R/LAnkleWidth
     - Foot length may be inexact during visualization in director.
       Joint angles are unaffected
     - Only lower-limb bones are currently created
    """

    # Repeat for right and left sides
    sides = ['R', 'L']
    for side in sides:

        if side == 'R':
            sign = 1
        elif side == 'L':
            sign = -1

        # =======================================================================
        # Create tibia segments
        # =======================================================================

        # Extract marker for the tibia relative to the lab
        ANK = data[side + 'ANK']
        MMA = data[side + 'MMA']
        TUB = data[side + 'TUB']
        HFB = data[side + 'HFB']

        # Create LabTibia origin
        LabTIB0 = (MMA + ANK) / 2

        # Project TUB onto the plane of MMA, ANK, HFB
        PROT = point_to_plane(TUB, MMA, ANK, HFB)

        if side + 'KneeJC' in data:
            KneeJC = data[side + 'KneeJC']
        else:
            KneeJC = PROT

        if version == '1.0':
            AnkleJC = data[side + 'AnkleJC']
            TIR = data[side + 'TIR']
        elif version == '1.1':
            AnkleJC = (data[side + 'ANK'] + data[side + 'MMA']) / 2

        if version == '1.0':
            [TIB0, TIB1, TIB2, TIB3, _] = create_lcs(AnkleJC, KneeJC - AnkleJC, sign * (AnkleJC - TIR), 'zxy')
        elif version == '1.1':
            [TIB0, TIB1, TIB2, TIB3, _] = create_lcs(AnkleJC, KneeJC - AnkleJC, sign * (MMA - ANK), 'yxz')

        # Add to struct
        data[side + 'TIB0'] = TIB0
        data[side + 'TIB1'] = TIB1
        data[side + 'TIB2'] = TIB2
        data[side + 'TIB3'] = TIB3

        # =======================================================================
        # Create tibia relative to the lab ( TibiaLab)
        # =======================================================================
        #
        # Create LabTibia axes
        if version == '1.0':
            [LabTIB0, LabTIB1, LabTIB2, LabTIB3, _] = create_lcs(LabTIB0, PROT - LabTIB0, sign * (MMA - ANK), 'zxy')
        elif version == '1.1':
            [LabTIB0, LabTIB1, LabTIB2, LabTIB3] = [TIB0, TIB1, TIB2, TIB3]

        # Add as new channels
        data[side + 'LabTIB0'] = LabTIB0
        data[side + 'LabTIB1'] = LabTIB1
        data[side + 'LabTIB2'] = LabTIB2
        data[side + 'LabTIB3'] = LabTIB3

        # =======================================================================
        # Create hindfoot segment
        # =======================================================================

        # Extract markers
        PCA = data[side + 'PCA']
        HEE = data[side + 'HEE']
        HFPlantar = data[side + 'HFPlantar']


        # Create hindfoot axes
        if version == '1.0':
            [HDF0, HDF1, HDF2, HDF3, _] = create_lcs(HEE, HFPlantar - HEE, PCA - HEE, 'zyx')
        elif version == '1.1':
            [HDF0, HDF1, HDF2, HDF3, _] = create_lcs(HEE, HFPlantar - HEE, PCA - HEE, 'xzy')

        # Add as new channels
        data[side + 'HDF0'] = HDF0
        data[side + 'HDF1'] = HDF1
        data[side + 'HDF2'] = HDF2
        data[side + 'HDF3'] = HDF3

        # =======================================================================
        # Create forefoot segment
        # =======================================================================

        # Extract markers
        P1M = data[side + 'P1M']
        P5M = data[side + 'P5M']
        D1M0 = data[side + 'D1M0']
        D5M0 = data[side + 'D5M0']
        TOE = data[side + 'TOE']

        # Create virtual markers
        projTOE = point_to_plane(TOE, D1M0, D5M0, P5M)
        projP1M = point_to_plane(P1M, D1M0, D5M0, P5M)

        P1P5dist = magnitude(projP1M - P5M)
        markerdiam = data['parameters']['PROCESSING']['MarkerDiameter']['value']
        proxFFscale = (P1P5dist - (markerdiam / 2)) / (2 * P1P5dist)
        proxFF = pointonline(projP1M, P5M, proxFFscale)

        # Find arch height
        # Extract virtual markers for the ArchHeightIndex
        P1Mlat = data[side + 'P1Mlat']
        D1Mlat = data[side + 'D1Mlat']
        D5Mlat = data[side + 'D5Mlat']
        FootLength = data['parameters']['PROCESSING']['%' + side + 'FootLength_openOFM']['value']

        # Calculate the ArchHeightIndex
        projP1M0lat = point_to_plane(P1Mlat, D1Mlat, D5Mlat, P5M)
        # projP1M0lat = point_to_plane(P1Mlat, D1Mlat, D5M0, P5M)
        # ArchHeightIndex = np.linalg.norm(projP1M0lat - P1M, axis=1) / FootLength * 100
        ArchHeightIndex = magnitude(projP1M0lat - P1M) / FootLength * 100
        ArchHeight = np.array((np.zeros(np.shape(ArchHeightIndex)),

                               np.zeros(np.shape(ArchHeightIndex)),
                               ArchHeightIndex)).T

        # Create forefoot axes
        if version == '1.0':
            FOF0, FOF1, FOF2, FOF3, _ = create_lcs(projTOE, projTOE - proxFF, sign * (D1M0 - D5M0), 'zxy')
        if version == '1.1':
            FOF0, FOF1, FOF2, FOF3, _ = create_lcs(projTOE, projTOE - proxFF, sign * (D5M0 - D1M0), 'xyz')

        # Add as new channels
        data[side + 'FOF0'] = FOF0
        data[side + 'FOF1'] = FOF1
        data[side + 'FOF2'] = FOF2
        data[side + 'FOF3'] = FOF3
        data[side + 'ArchHeightIndex'] = ArchHeightIndex
        data[side + 'ArchHeight_openOFM'] = ArchHeight

        # =======================================================================
        # Create hallux segment
        # =======================================================================

        # Extract markers
        HLX = data[side + 'HLX']

        # Create hallux axes
        if version == '1.0':
            [HLX0, HLX1, HLX2, HLX3, _] = create_lcs(D1M0, HLX - D1M0, sign * (D1M0 - D5M0), 'zxy')
        if version == '1.1':
            [HLX0, HLX1, HLX2, HLX3, _] = create_lcs(D1M0, HLX - D1M0, FOF3-FOF0, 'yxz')


        # Add as new channels
        data[side + 'HLX0'] = HLX0
        data[side + 'HLX1'] = HLX1
        data[side + 'HLX2'] = HLX2
        data[side + 'HLX3'] = HLX3

    r, jnt, data = getbones_data(data)

    return data, r, jnt
