import numpy as np
from linear_algebra.linear_algebra import static2dynamic, create_lcs, point_to_plane, replace4, \
    move_marker_gcs_2_lcs, magnitude
from utils.utils import getDirStat


def create_virtual_markers(sdata, settings):
    # Check if settings argument is provided, otherwise set it to an empty dictionary

    version = settings['version']
    processing = settings['processing']

    # Define sides
    sides = ['R', 'L']

    # Iterate over sides
    for side in sides:

        # Determine whether to use HE1 or HEE marker for the hindfoot
        HE1_sta = sdata.get(side + 'HE1', sdata[side + 'HEE'])
        processing['Has' + side + 'HE1'] = side + 'HE1' in sdata

        HE0_sta = HE1_sta

        # FOREFOOT -------------

        # Extract markers from static trial
        marker_names = ['D1M', 'D5M', 'P5M', 'P1M', 'TOE']
        D1M_sta, D5M_sta, P5M_sta, P1M_sta, TOE_sta = [sdata[f"{side}{name}"] for name in marker_names]

        # correct position of markers (replace 4)
        if version == '1.0':
            P1M_sta, D5M_sta, TOE_sta, P5M_sta = replace4(P1M_sta, D5M_sta, TOE_sta, P5M_sta)

        # create technical forefoot axes (Dummy in BodyBuilder)
        O_sta, A_sta, L_sta, P_sta, _ = create_lcs(P1M_sta, P1M_sta - D5M_sta, TOE_sta - P5M_sta, 'xyz')

        # create forefoot virtual markers from static trial
        D1M0 = np.column_stack((D1M_sta[:, 0], D1M_sta[:, 1], P5M_sta[:, 2])) if processing[side + 'UseFloorFF'] else D1M_sta
        D5M0 = np.column_stack((D5M_sta[:, 0], D5M_sta[:, 1], P5M_sta[:, 2])) if processing[side + 'UseFloorFF'] else D5M_sta

        # express forefoot virtual markers in LCS of static trial
        D1M0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D1M0)
        D5M0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D5M0)

        # round out errors and add to parameter list
        for marker, data_lcl, names in [
            ('D1M0', D1M0_lcl, ['D1M0X_openOFM', 'D1M0Y_openOFM', 'D1M0Z_openOFM']),
            ('D5M0', D5M0_lcl, ['D5M0X_openOFM', 'D5M0Y_openOFM', 'D5M0Z_openOFM'])
        ]:
            data_av = np.expand_dims(np.mean(data_lcl, axis=0), axis=0)
            for i, name in enumerate(names):
                sdata['parameters']['PROCESSING']['%' + side + name] = data_av[0, i]

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
        static_markers = ['PCA', 'HEE', 'STL', 'LCA', 'P5M', 'CPG']
        PCA_sta, HEE_sta, STL_sta, LCA_sta, P5M_sta, CPG_sta = [sdata[f"{side}{m}"] for m in static_markers]

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
                direction = getDirStat(sdata, settings)
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
        marker_names = ['ANK', 'MMA', 'HFB', 'SHN', 'TUB']# MMA marker only present in static trials
        ANK_sta, MMA_sta, HFB_sta, SHN_sta, TUB_sta = [sdata[f"{side}{m}"] for m in marker_names]

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
        D1M0 = np.array([data['parameters']['PROCESSING']['%' + side + f'D1M0{axis}_openOFM']['value'] 
                        for axis in ['X', 'Y', 'Z']])
        D5M0 = np.array([data['parameters']['PROCESSING']['%' + side + f'D5M0{axis}_openOFM']['value'] 
                        for axis in ['X', 'Y', 'Z']])
        
        # Extract markers from dynamic trial
        D5M_dyn, P5M_dyn, P1M_dyn, TOE_dyn = (data[side + name] for name in ['D5M', 'P5M', 'P1M', 'TOE'])

        # # keep original D5M marker for replace4 in segments
        # data[side + 'D5M'] = D5M_dyn

        # correct position of markers (replace 4)
        if version == '1.0':
            P1M_dyn, D5M_dyn, TOE_dyn, P5M_dyn = replace4(P1M_dyn, D5M_dyn, TOE_dyn, P5M_dyn)

        # create technical forefoot axes (Dummy in BodyBuilder)
        O_dyn, A_dyn, L_dyn, P_dyn, _ = create_lcs(P1M_dyn, P1M_dyn - D5M_dyn, TOE_dyn - P5M_dyn, 'xyz')

        D1M0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D1M0)

        # D5M is physical marker
        D5M0_dyn = (
            static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D5M0) 
            if processing[f"{side}UseFloorFF"] 
            else D5M_dyn
        )

        for name, value in [('D1M0', D1M0_dyn), ('D5M0', D5M0_dyn), ('P1M', P1M_dyn), ('P5M', P5M_dyn), ('TOE', TOE_dyn)]:
            data[side + name] = value

        # Lateral Forefoot
        # create technical lateral forefoot axes
        O_dyn, A_dyn, L_dyn, P_dyn, _ = create_lcs(P5M_dyn, D5M_dyn - P5M_dyn, TOE_dyn - D5M_dyn, 'xyz')

        # get static
        proc_params = data['parameters']['PROCESSING']
        def get_static_offset(name):
            return np.array([
                proc_params[f"%{side}{name}{axis}_openOFM"]['value'] 
                for axis in 'XYZ'
            ])
        D1Mlat0, P1Mlat0, D5Mlat0 = [get_static_offset(m) for m in ['D1Mlat', 'P1Mlat', 'D5Mlat']]

        # create dynamic version of static marker and add as virtual marker
        D1Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D1Mlat0)
        P1Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, P1Mlat0)
        D5Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D5Mlat0)

        data[side + 'D1Mlat'] = D1Mlat_dyn
        data[side + 'P1Mlat'] = P1Mlat_dyn
        data[side + 'D5Mlat'] = D5Mlat_dyn

        # Hindfoot
        # extract markers from static trials
        proc_params = data['parameters']['PROCESSING']

        def get_static_vec(name):
            return np.array([
                proc_params[f"%{side}{name}{axis}_openOFM"]['value'] 
                for axis in 'XYZ'
            ])
        PCA0_sta = get_static_vec('PCA0') # PCA marker only present in static trials
        HFPlantar_sta = get_static_vec('HFPlantar')

        # extract markers from dynamic trials
        marker_keys = ['STL', 'LCA', 'CPG', 'HEE']
        STL_dyn, LCA_dyn, CPG_dyn, HE0_dyn = [data[f"{side}{k}"] for k in marker_keys]

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
        ANK_dyn, HFB_dyn, SHN_dyn, TUB_dyn = (data[side + name] for name in ['ANK', 'HFB', 'SHN', 'TUB'])

        # correct position of markers
        if version == '1.0':
            ANK_dyn, HFB_dyn, TUB_dyn, SHN_dyn = replace4(ANK_dyn, HFB_dyn, TUB_dyn, SHN_dyn)

        # create local coordinate systems
        O_dyn, A_dyn, L_dyn, P_dyn, _ = create_lcs(ANK_dyn, HFB_dyn - ANK_dyn, SHN_dyn - ((ANK_dyn + HFB_dyn) / 2),
                                                   'xyz')

        # create dynamic version of static marker
        MMA0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, MMA0)

        # add dynamic marker to dynamic trial
        for name, value in [('MMA', MMA0_dyn), ('ANK', ANK_dyn), ('TUB', TUB_dyn), ('HFB', HFB_dyn)]:
            data[side + name] = value

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
