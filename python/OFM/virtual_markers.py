import numpy as np
from linear_algebra.linear_algebra import static2dynamic, create_lcs, point_to_plane, replace4, \
    move_marker_gcs_2_lcs, magnitude
from utils.utils import getDir


def create_virtual_markers(sdata, settings):
    # Check if settings argument is provided, otherwise set it to an empty dictionary

    version = settings['version']

    processing = settings['processing']

    # Define sides
    sides = ['R', 'L']

    # Iterate over sides
    for side in sides:

        # Determine whether to use HE1 or HEE marker for the hindfoot
        if side + 'HE1' in sdata:
            HE1_sta = sdata[side + 'HE1']
            processing['Has' + side + 'HE1'] = True
        else:
            HEE_sta = sdata[side + 'HEE']
            HE1_sta = HEE_sta
            processing['Has' + side + 'HE1'] = False

        HE0_sta = HE1_sta

        # FOREFOOT -------------

        # Extract markers from static trial
        D1M_sta = sdata[side + 'D1M']
        D5M_sta = sdata[side + 'D5M']
        P5M_sta = sdata[side + 'P5M']
        P1M_sta = sdata[side + 'P1M']
        TOE_sta = sdata[side + 'TOE']

        # correct position of markers (replace 4)
        if version == '1.0':
            P1M_sta, D5M_sta, TOE_sta, P5M_sta = replace4(P1M_sta, D5M_sta, TOE_sta, P5M_sta)

        # create technical forefoot axes (Dummy in BodyBuilder)
        O_sta, A_sta, L_sta, P_sta, _ = create_lcs(P1M_sta, P1M_sta - D5M_sta, TOE_sta - P5M_sta, 'xyz')

        # create forefoot virtual markers from static trial
        if processing[side + 'UseFloorFF']:
            D1M0 = np.column_stack((D1M_sta[:, 0], D1M_sta[:, 1], P5M_sta[:, 2]))
            D5M0 = np.column_stack((D5M_sta[:, 0], D5M_sta[:, 1], P5M_sta[:, 2]))
        else:
            D1M0 = D1M_sta
            D5M0 = D5M_sta

        # express forefoot virtual markers in LCS of static trial
        D1M0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D1M0)
        D5M0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D5M0)

        # round out errors and add to parameter list
        D1M0_lcl_av = np.expand_dims(np.mean(D1M0_lcl, axis=0), axis=0)
        D1M0_openOFMs = ['D1M0X_openOFM', 'D1M0Y_openOFM', 'D1M0Z_openOFM']
        for i, D1M0_openOFM in enumerate(D1M0_openOFMs):
            sdata['parameters']['PROCESSING']['%' + side + D1M0_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + D1M0_openOFM] = D1M0_lcl_av[0, i]

        D5M0_lcl_av = np.expand_dims(np.mean(D5M0_lcl, axis=0), axis=0)
        D5M0_openOFMs = ['D5M0X_openOFM', 'D5M0Y_openOFM', 'D5M0Z_openOFM']
        for i, D5M0_openOFM in enumerate(D5M0_openOFMs):
            sdata['parameters']['PROCESSING']['%' + side + D5M0_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + D5M0_openOFM] = D5M0_lcl_av[0, i]

        # Lateral Forefoot - not yet supported
        # create technical lateral forefoot axes
        O_sta, A_sta, L_sta, P_sta, _ = create_lcs(P5M_sta, D5M_sta - P5M_sta, TOE_sta - D5M_sta, 'xyz')

        # create lateral forefoot virtual markers from static trial
        D1Mlat = D1M0
        P1Mlat = P1M_sta
        D5Mlat = D5M_sta

        # express lateral forefoot virtual markers in LCS of static trial
        D1Mlat_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D1Mlat)
        P1Mlat_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, P1Mlat)
        D5Mlat_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D5Mlat)

        # round out errors and add to parameter list
        D1Mlat_lcl_av = np.mean(D1Mlat_lcl, axis=0)
        P1Mlat_lcl_av = np.mean(P1Mlat_lcl, axis=0)
        D5Mlat_lcl_av = np.mean(D5Mlat_lcl, axis=0)

        D1Mlats_openOFM = ['D1MlatX_openOFM', 'D1MlatY_openOFM', 'D1MlatZ_openOFM']
        for i, D1Mlat_openOFM in enumerate(D1Mlats_openOFM):
            sdata['parameters']['PROCESSING']['%' + side + D1Mlat_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + D1Mlat_openOFM] = D1Mlat_lcl_av[i]

        P1Mlats_openOFM = ['P1MlatX_openOFM', 'P1MlatY_openOFM', 'P1MlatZ_openOFM']
        for i, P1Mlat_openOFM in enumerate(P1Mlats_openOFM):
            sdata['parameters']['PROCESSING']['%' + side + P1Mlat_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + P1Mlat_openOFM] = P1Mlat_lcl_av[i]

        D5Mlats_openOFM = ['D5MlatX_openOFM', 'D5MlatY_openOFM', 'D5MlatZ_openOFM']
        for i, D5Mlat_openOFM in enumerate(D5Mlats_openOFM):
            sdata['parameters']['PROCESSING']['%' + side + D5Mlat_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + D5Mlat_openOFM] = D5Mlat_lcl_av[i]

        # Hindfoot
        # extract markers from static trials
        PCA_sta = sdata[side + 'PCA']  # PCA marker only present in static trials
        HEE_sta = sdata[side + 'HEE']
        STL_sta = sdata[side + 'STL']
        LCA_sta = sdata[side + 'LCA']
        P5M_sta = sdata[side + 'P5M']
        CPG_sta = sdata[side + 'CPG']

        # correct position of markers
        if version == '1.0':
            HE0_sta, LCA_sta, STL_sta, _ = replace4(HE0_sta, LCA_sta, STL_sta, CPG_sta)

        # create technical hindfoot axes
        O_sta, A_sta, L_sta, P_sta, _ = create_lcs(HE0_sta, HE0_sta - ((STL_sta + LCA_sta) / 2), STL_sta - LCA_sta,
                                                   'xyz')

        # create virtual marker PCA0
        PCA0 = PCA_sta

        # create HFPlantar virtual marker
        midcal = (STL_sta + LCA_sta) / 2
        projP5M = point_to_plane(P5M_sta, HE0_sta, PCA_sta, midcal)

        # adjust HFPlantar depending if flat or not flat foot
        if processing[side + 'HindFootFlat']:

            if version == '1.0':
                HFPlantar = np.vstack((projP5M[:, 0], projP5M[:, 1], HE0_sta[:, 2])).T
            else:
                # todo: check based on manuscript
                # the anterior vector becomes the intersection of the mid-sagittal plane with
                # a plane parallel to the floor
                direction = getDir(sdata)
                if direction in ['Ipos', 'Ineg']:
                    [O, _, lat_ax, _, _] = create_lcs(HE1_sta, midcal - HE1_sta, PCA_sta - HE1_sta, 'xyz')
                    lat_ax = lat_ax - O
                    dir_z = np.array([-lat_ax[:, 1], lat_ax[:, 0], np.zeros(np.shape(lat_ax[:, 1]))]).T
                    HFPlantar = HE1_sta + dir_z
                elif direction in ['Jpos', 'Jneg']:
                    [O, lat_ax, _, _, _] = create_lcs(HE1_sta, midcal - HE1_sta, PCA_sta - HE1_sta, 'yxz')
                    lat_ax = lat_ax - O
                    dir_z = np.array([lat_ax[:, 1], -lat_ax[:, 0], np.zeros(np.shape(lat_ax[:, 1]))]).T
                    HFPlantar = HE1_sta + dir_z

        else:
            HFPlantar = projP5M
            if not processing['Has' + side + 'HE1']:
                HE1_sta = (HEE_sta + PCA0) / 2
                sdata[side + 'HEE'] = HEE_sta  # true HEE marker shift
                sdata[side + 'HE1'] = HE1_sta  # saved HE1, which is OG HEE

        # express hindfoot virtual markers in LCS of static trial
        PCA0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, PCA0)
        HFPlantar_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, HFPlantar)

        # round out errors and add to parameter list
        PCA0_lcl_av = np.expand_dims(np.mean(PCA0_lcl, axis=0), axis=0)
        PCA0_openOFMs = ['PCA0X_openOFM', 'PCA0Y_openOFM', 'PCA0Z_openOFM']
        for i, PCA0_openOFM in enumerate(PCA0_openOFMs):
            sdata['parameters']['PROCESSING']['%' + side + PCA0_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + PCA0_openOFM] = PCA0_lcl_av[0, i]

        HFPlantar_lcl_av = np.expand_dims(np.mean(HFPlantar_lcl, axis=0), axis=0)
        HFPlantar_openOFMs = ['HFPlantarX_openOFM', 'HFPlantarY_openOFM', 'HFPlantarZ_openOFM']
        for i, HFPlantar_openOFM in enumerate(HFPlantar_openOFMs):
            sdata['parameters']['PROCESSING']['%' + side + HFPlantar_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + HFPlantar_openOFM] = HFPlantar_lcl_av[0, i]

        # Tibia
        # extract markers from static trials
        ANK_sta = sdata[side + 'ANK']
        MMA_sta = sdata[side + 'MMA']  # MMA marker only present in static trials
        HFB_sta = sdata[side + 'HFB']
        SHN_sta = sdata[side + 'SHN']
        TUB_sta = sdata[side + 'TUB']

        # correct position of markers
        if version == '1.0':
            ANK_sta, HFB_sta, _, SHN_sta = replace4(ANK_sta, HFB_sta, TUB_sta, SHN_sta)

        # create local coordinate systems
        O_sta, A_sta, L_sta, P_sta, _ = create_lcs(ANK_sta, HFB_sta - ANK_sta, SHN_sta - ((ANK_sta + HFB_sta) / 2),
                                                   'xyz')

        # create tibia virtual markers
        MMA0 = MMA_sta

        # express RMMA_stat in lcs static
        MMA0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, MMA0)

        # round out errors and add to parameters
        MMA0_lcl_av = np.mean(MMA0_lcl, axis=0)

        MMAs_openOFM = ['MMAX_openOFM', 'MMAY_openOFM', 'MMAZ_openOFM']
        for i, MMA_openOFM in enumerate(MMAs_openOFM):
            sdata['parameters']['PROCESSING']['%' + side + MMA_openOFM] = {}
            sdata['parameters']['PROCESSING']['%' + side + MMA_openOFM] = MMA0_lcl_av[i]

        # Parameters
        TOE_sta = sdata[side + 'TOE']

        # Define Foot Length
        FootLength = np.mean(magnitude(HEE_sta - TOE_sta))

        # Calculate the ArchHeightIndex
        projP1M0lat = point_to_plane(P1Mlat,   D1Mlat, D5M_sta, P5M_sta)
        ArchHeightIndex = np.linalg.norm(projP1M0lat - P1M_sta, axis=1) / FootLength * 100
        ArchHeight = np.array((np.zeros(np.shape(ArchHeightIndex)),
                               np.zeros(np.shape(ArchHeightIndex)),
                               ArchHeightIndex)).T

        sdata['parameters']['PROCESSING']['%' + side + 'FootLength_openOFM'] = FootLength
        sdata[side + 'ArchHeight_openOFM'] = ArchHeight

    return sdata


def animate_virtual_markers(data, settings):
    # Check if settings argument is provided, otherwise set it to an empty dictionary

    if settings is None:
        settings = {}

    processing = settings['processing']
    version = settings['version']

    # Define sides
    sides = ['R', 'L']

    # Iterate over sides
    for side in sides:

        # FOREFOOT -------------

        # Extract virtual markers saved from static trial
        D1M0 = np.array([data['parameters']['PROCESSING']['%' + side + 'D1M0X_openOFM']['value'],
                         data['parameters']['PROCESSING']['%' + side + 'D1M0Y_openOFM']['value'],
                         data['parameters']['PROCESSING']['%' + side + 'D1M0Z_openOFM']['value'],
                         ])
        D5M0 = np.array([data['parameters']['PROCESSING']['%' + side + 'D5M0X_openOFM']['value'],
                         data['parameters']['PROCESSING']['%' + side + 'D5M0Y_openOFM']['value'],
                         data['parameters']['PROCESSING']['%' + side + 'D5M0Z_openOFM']['value'],
                         ])
        # Extract markers from dynamic trial
        D5M_dyn = data[side + 'D5M']
        P5M_dyn = data[side + 'P5M']
        P1M_dyn = data[side + 'P1M']
        TOE_dyn = data[side + 'TOE']

        # # keep original D5M marker for replace4 in segments
        # data[side + 'D5M'] = D5M_dyn

        # correct position of markers (replace 4)
        if version == '1.0':
            P1M_dyn, D5M_dyn, TOE_dyn, P5M_dyn = replace4(P1M_dyn, D5M_dyn, TOE_dyn, P5M_dyn)

        # create technical forefoot axes (Dummy in BodyBuilder)
        O_dyn, A_dyn, L_dyn, P_dyn, _ = create_lcs(P1M_dyn, P1M_dyn - D5M_dyn, TOE_dyn - P5M_dyn, 'xyz')

        D1M0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D1M0)

        # D5M is physical marker
        if processing[side + 'UseFloorFF']:
            D5M0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D5M0)
        else:
            D5M0_dyn = D5M_dyn

        data[side + 'D1M0'] = D1M0_dyn
        data[side + 'D5M0'] = D5M0_dyn
        data[side + 'P1M'] = P1M_dyn
        data[side + 'P5M'] = P5M_dyn
        data[side + 'TOE'] = TOE_dyn

        # Lateral Forefoot
        # create technical lateral forefoot axes
        O_dyn, A_dyn, L_dyn, P_dyn, _ = create_lcs(P5M_dyn, D5M_dyn - P5M_dyn, TOE_dyn - D5M_dyn, 'xyz')

        # get static
        D1Mlat0 = np.array([data['parameters']['PROCESSING']['%' + side + 'D1MlatX_openOFM']['value'],
                            data['parameters']['PROCESSING']['%' + side + 'D1MlatY_openOFM']['value'],
                            data['parameters']['PROCESSING']['%' + side + 'D1MlatZ_openOFM']['value'],
                            ])
        P1Mlat0 = np.array([data['parameters']['PROCESSING']['%' + side + 'P1MlatX_openOFM']['value'],
                            data['parameters']['PROCESSING']['%' + side + 'P1MlatY_openOFM']['value'],
                            data['parameters']['PROCESSING']['%' + side + 'P1MlatZ_openOFM']['value'],
                            ])
        D5Mlat0 = np.array([data['parameters']['PROCESSING']['%' + side + 'D5MlatX_openOFM']['value'],
                            data['parameters']['PROCESSING']['%' + side + 'D5MlatY_openOFM']['value'],
                            data['parameters']['PROCESSING']['%' + side + 'D5MlatZ_openOFM']['value'],
                            ])

        # create dynamic version of static marker and add as virtual marker
        D1Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D1Mlat0)
        P1Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, P1Mlat0)
        D5Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D5Mlat0)

        data[side + 'D1Mlat'] = D1Mlat_dyn
        data[side + 'P1Mlat'] = P1Mlat_dyn
        data[side + 'D5Mlat'] = D5Mlat_dyn

        # Hindfoot
        # extract markers from static trials
        PCA0_sta = np.array([data['parameters']['PROCESSING']['%' + side + 'PCA0X_openOFM']['value'],
                             data['parameters']['PROCESSING']['%' + side + 'PCA0Y_openOFM']['value'],
                             data['parameters']['PROCESSING']['%' + side + 'PCA0Z_openOFM']['value'],
                             ])  # PCA marker only present in static trials
        HFPlantar_sta = np.array([data['parameters']['PROCESSING']['%' + side + 'HFPlantarX_openOFM']['value'],
                                  data['parameters']['PROCESSING']['%' + side + 'HFPlantarY_openOFM']['value'],
                                  data['parameters']['PROCESSING']['%' + side + 'HFPlantarZ_openOFM']['value'],
                                  ])

        # extract markers from dynamic trials
        STL_dyn = data[side + 'STL']
        LCA_dyn = data[side + 'LCA']
        CPG_dyn = data[side + 'CPG']
        HE0_dyn = data[side + 'HEE']

        # correct position of markers
        if version == '1.0':
            HE0_dyn, LCA_dyn, STL_dyn, _ = replace4(HE0_dyn, LCA_dyn, STL_dyn, CPG_dyn)

        # create technical hindfoot axes
        O_dyn, A_dyn, L_dyn, P_dyn, _ = create_lcs(HE0_dyn, HE0_dyn - ((STL_dyn + LCA_dyn) / 2), STL_dyn - LCA_dyn,
                                                   'xyz')

        # create dynamic version of static marker
        PCA0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, PCA0_sta)
        HFPlantar_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, HFPlantar_sta)

        # add as virtual marker
        data[side + 'PCA'] = PCA0_dyn
        data[side + 'HFPlantar'] = HFPlantar_dyn
        data[side + 'HEE'] = HE0_dyn

        # Tibia
        # extract markers from static trials
        MMA0 = np.array([data['parameters']['PROCESSING']['%' + side + 'MMAX_openOFM']['value'],
                         data['parameters']['PROCESSING']['%' + side + 'MMAY_openOFM']['value'],
                         data['parameters']['PROCESSING']['%' + side + 'MMAZ_openOFM']['value'],
                         ])

        # extract markers from dynamic trials
        ANK_dyn = data[side + 'ANK']
        HFB_dyn = data[side + 'HFB']
        SHN_dyn = data[side + 'SHN']
        TUB_dyn = data[side + 'TUB']

        # correct position of markers
        if version == '1.0':
            ANK_dyn, HFB_dyn, TUB_dyn, SHN_dyn = replace4(ANK_dyn, HFB_dyn, TUB_dyn, SHN_dyn)

        # create local coordinate systems
        O_dyn, A_dyn, L_dyn, P_dyn, _ = create_lcs(ANK_dyn, HFB_dyn - ANK_dyn, SHN_dyn - ((ANK_dyn + HFB_dyn) / 2),
                                                   'xyz')

        # create dynamic version of static marker
        MMA0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, MMA0)

        # add dynamic marker to dynamic trial
        data[side + 'MMA'] = MMA0_dyn
        data[side + 'ANK'] = ANK_dyn
        data[side + 'TUB'] = TUB_dyn
        data[side + 'HFB'] = HFB_dyn

        # Find arch height
        # Extract virtual markers for the ArchHeightIndex(from ofm_static2dynamic_data)
        P1Mlat = data[side + 'P1Mlat']
        D1Mlat = data[side + 'D1Mlat']
        FootLength = data['parameters']['PROCESSING']['%' + side + 'FootLength_openOFM']['value']

        # Calculate the ArchHeightIndex
        projP1M0lat = point_to_plane(P1Mlat, D1Mlat, D5M0_dyn, P5M_dyn)
        ArchHeightIndex = np.linalg.norm(projP1M0lat - P1M_dyn, axis=1) / FootLength * 100
        ArchHeight = np.array((np.zeros(np.shape(ArchHeightIndex)),
                               np.zeros(np.shape(ArchHeightIndex)),
                               ArchHeightIndex)).T

        # add dynamic marker to dynamic trial
        data[side + 'ArchHeight'] = ArchHeight

    return data
