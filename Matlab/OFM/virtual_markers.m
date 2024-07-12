function data = virtual_markers(data, sdata, settings, version)

% data = MAKE_VIRTUAL_MARKERS(data, sdata, settings)
%
% creates virtual static markers in dynamic trial (data) based on position
% of static markers in static trial (sdata)
%
% ARGUMENTS
%   data     ... struct. Dynamic trial data
%   sdata    ... struct, static trial data
%   settings ... struct, information to guide computational options
%                settings.RHindFootFlat (default=True), If true, assumes
%                right foot makes contact with ground during static trial
%                settings.LHindFootFlat (default=True), If true, assumes
%                left foot makes contact with ground during static trial
%
% RETURNS
%   data    ... struct, Dynamic trial data with appended static markers
%
% NOTES
% - static markers added to dynamic trial:
%   R/LD1M, R/LPCA, R/LMMA
% - additional outputs:
%   R/LHFAnterior
%   R/LHFPlantar

%=======================================================================%
% SET DEFAULTS
%=======================================================================%
if nargin == 2
    settings = struct;
end
if version == "1.0"
    settings.replace4 = true;
else
    settings.replace4 = false;
end
sides = {'R','L'};        
    for j = 1:length(sides)
        side = sides{j};
    
        if ~isfield(settings, [side,'HindFootFlat']) %flag
            settings.([side,'HindFootFlat']) = true;
        end
        
        
        % move HEE marker when hindfoot not flat 
        if isfield(sdata, [side,'HE1'])
            HE1_sta = sdata.([side,'HE1']);
            settings.(['Has',side,'HE1']) = true;      % if HE1 already exists, set HasRHE1 to true
        else
            HEE_sta = sdata.([side,'HEE']);
            HE1_sta = HEE_sta;                  % if it does not exist, make HE1 = HEE
            settings.(['Has',side,'HE1']) = false;
        end
        HE0_sta = HE1_sta;
        
        if isfield(data, [side,'HE1'])
            HE1_dyn = data.([side,'HE1']);
            settings.(['Has',side,'HE1']) = true;      % if HE1 already exists, set HasRHE1 to true
        else
            HE1_dyn = data.([side,'HEE']);          % if it does not exist, make HE1 = HEE
        end
        % HE0_dyn = v_data.([side,'HDF0']);
        HE0_dyn = HE1_dyn;
        
        %=======================================================================%
        % Forefoot
        %=======================================================================%
        
        % extract markers from static trials
        D1M_sta = sdata.([side,'D1M']); % D1M marker only present in static trials
        D5M_sta = sdata.([side,'D5M']);
        P5M_sta = sdata.([side,'P5M']);
        P1M_sta = sdata.([side,'P1M']);
        TOE_sta = sdata.([side,'TOE']);
        
        % extract markers from dynamic trials
        D5M_dyn = data.([side,'D5M']);
        P5M_dyn = data.([side,'P5M']);
        P1M_dyn = data.([side,'P1M']);
        TOE_dyn = data.([side,'TOE']);
        
        % keep original D5M marker for replace4 in ofm_makebones_data
        data.([side,'D5M0']) = D5M_dyn;
        
        % correct position of markers
        if settings.replace4 == true
            [P1M_sta,D5M_sta,TOE_sta,P5M_sta] = replace4(P1M_sta,D5M_sta,TOE_sta,P5M_sta);
            [P1M_dyn,D5M_dyn,TOE_dyn,P5M_dyn] = replace4(P1M_dyn,D5M_dyn,TOE_dyn,P5M_dyn);
        end
        
        % create technical forefoot axes (Dummy in BodyBuilder)
        [O_sta, A_sta, L_sta, P_sta, ~] = create_lcs(P1M_sta, P1M_sta-D5M_sta, TOE_sta-P5M_sta,'xyz');
        [O_dyn, A_dyn, L_dyn, P_dyn, ~] = create_lcs(P1M_dyn, P1M_dyn-D5M_dyn, TOE_dyn-P5M_dyn,'xyz');
        

        % create forefoot virtual markers from static trial
        if settings.([side,'UseFloorFF']) == true % Find projection of proximal FF and TOE on plantar surface of FF
            D1M0 = [D1M_sta(:,1),D1M_sta(:,2),P5M_sta(:,3)];
            D5M0 = [D5M_sta(:,1),D5M_sta(:,2),P5M_sta(:,3)];
        else
            D1M0 = D1M_sta;
            D5M0 = D5M_sta;
        end
        
        % express forefoot virtual markers in LCS of static trial
        D1M0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D1M0);
        
        if settings.([side,'UseFloorFF']) == true
            D5M0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D5M0);
        end
        
        % round out errors and add to parameter list
        D1M0_lcl_av = mean(D1M0_lcl);
        
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D1M0X_openOFM']).data = D1M0_lcl_av(1);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D1M0Y_openOFM']).data = D1M0_lcl_av(2);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D1M0Z_openOFM']).data = D1M0_lcl_av(3);
        
        if settings.([side,'UseFloorFF']) == true
            D5M0_lcl_av = mean(D5M0_lcl);
        
            data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D5M0X_openOFM']).data = D5M0_lcl_av(1);
            data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D5M0Y_openOFM']).data = D5M0_lcl_av(2);
            data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D5M0Z_openOFM']).data = D5M0_lcl_av(3);
        end
        
        % create dynamic version of static marker
        D1M0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D1M0_lcl_av);
        % add as new channel
        data.([side,'D1M']) = D1M0_dyn;
        
        if settings.([side,'UseFloorFF']) == true
            D5M0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D5M0_lcl_av);
            data.([side,'D5M']) = D5M0_dyn;
        end
        
        %=======================================================================%
        % Lateral Forefoot
        %=======================================================================%
        
        % create technical lateral forefoot axes
        [O_sta, A_sta, L_sta, P_sta, ~] = create_lcs(P5M_sta, D5M_sta-P5M_sta, TOE_sta-D5M_sta,'xyz');
        [O_dyn, A_dyn, L_dyn, P_dyn, ~] = create_lcs(P5M_dyn, D5M_dyn-P5M_dyn, TOE_dyn-D5M_dyn,'xyz');
        
        % create lateral forefoot virtual markers from static trial
        D1Mlat = D1M0;
        P1Mlat = P1M_sta;
        D5Mlat = D5M_sta;
        
        % express lateral forefoot virtual markers in LCS of static trial
        D1Mlat_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D1Mlat);
        P1Mlat_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, P1Mlat);
        D5Mlat_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, D5Mlat);
        
        % round out errors and add to parameter list
        D1Mlat_lcl_av = mean(D1Mlat_lcl);
        P1Mlat_lcl_av = mean(P1Mlat_lcl);
        D5Mlat_lcl_av = mean(D5Mlat_lcl);
        
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D1MlatX_openOFM']).data = D1Mlat_lcl_av(1);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D1MlatY_openOFM']).data = D1Mlat_lcl_av(2);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D1MlatZ_openOFM']).data = D1Mlat_lcl_av(3);
        
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'P1MlatX_openOFM']).data = P1Mlat_lcl_av(1);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'P1MlatY_openOFM']).data = P1Mlat_lcl_av(2);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'P1MlatZ_openOFM']).data = P1Mlat_lcl_av(3);
        
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D5MlatX_openOFM']).data = D5Mlat_lcl_av(1);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D5MlatY_openOFM']).data = D5Mlat_lcl_av(2);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'D5MlatZ_openOFM']).data = D5Mlat_lcl_av(3);
        
        % create dynamic version of static marker and add as virtual marker
        D1Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D1Mlat_lcl_av);
        P1Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, P1Mlat_lcl_av);
        D5Mlat_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, D5Mlat_lcl_av);
        
        data.([side,'D1Mlat']) = D1Mlat_dyn;
        data.([side,'P1Mlat']) = P1Mlat_dyn;
        data.([side,'D5Mlat']) = D5Mlat_dyn;
        
        %=======================================================================%
        % Hindfoot
        %=======================================================================%
        
        % extract markers from static trials
        PCA_sta = sdata.([side,'PCA']); % PCA marker only present in static trials
        HEE_sta = sdata.([side,'HEE']);
        STL_sta = sdata.([side,'STL']);
        LCA_sta = sdata.([side,'LCA']);
        P5M_sta = sdata.([side,'P5M']);
        CPG_sta = sdata.([side,'CPG']);
        
        % extract markers from dynamic trials
        STL_dyn = data.([side,'STL']);
        LCA_dyn = data.([side,'LCA']);
        CPG_dyn = data.([side,'CPG']);
        
        % correct position of markers
        if settings.replace4 == true
            [HE0_sta,LCA_sta,STL_sta,~] = replace4(HE0_sta,LCA_sta,STL_sta,CPG_sta);
            [HE0_dyn,LCA_dyn,STL_dyn,~] = replace4(HE0_dyn,LCA_dyn,STL_dyn,CPG_dyn);
        end
        
        % create technical hindfoot axes
        [O_sta,A_sta,L_sta,P_sta, ~] = create_lcs(HE0_sta, HE0_sta-((STL_sta + LCA_sta)/2), STL_sta - LCA_sta,'xyz');
        [O_dyn,A_dyn,L_dyn,P_dyn, ~] = create_lcs(HE0_dyn, HE0_dyn-((STL_dyn + LCA_dyn)/2), STL_dyn - LCA_dyn,'xyz');

        % create virtual marker PCA0
        PCA0 = PCA_sta;
        
        % create HFPlantar virtual marker
        midcal = (STL_sta + LCA_sta)/2;
        projP5M = point_to_plane(P5M_sta,HE0_sta,PCA_sta,midcal);
        
        % ajust HFPlantar depending if flat or not flat foot
        if settings.([side,'HindFootFlat']) == false
            HFPlantar = projP5M;
        
            if settings.(['Has',side,'HE1']) == false
                HE1_sta = (HEE_sta + PCA0)/2;
                sdata.([side,'HEE']) = HEE_sta; % true HEE marker shift
                sdata.([side,'HE1']) = HE1_sta; % saved HE1, which is OG HEE
            end
        else
            if version == "1.0"
                HFPlantar =  [projP5M(:,1), projP5M(:,2), HE0_sta(:,3)]; % default HE0 method for v1.0
            else
                % find normal to sagittal plane of HF
                [~,dir] = getDir(data);
                switch dir
                    case{'Ipos','Ineg'}
                        [O,dist_ax,lat_ax,~,~] = create_lcs(HE1_sta,midcal-HE1_sta, PCA_sta-HE1_sta, 'xyz');
                        lat_ax = lat_ax - O;
                        dist_dir = [-lat_ax(:,2),lat_ax(:,1),zeros(size(lat_ax(:,2)))];
                    case {'Jpos','Jneg'}
                        [O,lat_ax,dist_ax,~,~] = create_lcs(HE1_sta,midcal-HE1_sta, PCA_sta-HE1_sta, 'yxz');
                        lat_ax = lat_ax - O;
                        dist_dir = [lat_ax(:,2),-lat_ax(:,1),zeros(size(lat_ax(:,2)))];
                end
                O = O(1,:);
                lat_ax = lat_ax(1,:);
                dist_ax = dist_ax(1,:) - O;
                dist_ax = [dist_ax(:,1),dist_ax(:,2),zeros(size(dist_ax(:,2)))];
                dist_dir = dist_dir(1,:);
%                
%                 close all
%                 quiver3(O(1),O(2),O(3),lat_ax(1),lat_ax(2),lat_ax(3),'Color','g');
%                 hold on
%                 quiver3(O(1),O(2),O(3),dist_ax(1),dist_ax(2),dist_ax(3),'Color','c');
%                 quiver3(O(1),O(2),O(3),dist_dir(1),dist_dir(2),dist_dir(3),'Color','r');

                HFPlantar = HE1_sta + dist_dir;  % intersection of floor plane with sagittal HF plane is vector from RHE1 to RHFplantar
            end
        end
        
        % express hindfoot virtual markers in LCS of static trial
        PCA0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, PCA0);
        HFPlantar_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, HFPlantar);
        
        % round out errors and add to parameter list
        PCA0_lcl_av = mean(PCA0_lcl);
        HFPlantar_lcl_av = mean(HFPlantar_lcl);
        
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'PCAX_openOFM']).data = PCA0_lcl_av(1);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'PCAY_openOFM']).data = PCA0_lcl_av(2);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'PCAZ_openOFM']).data = PCA0_lcl_av(3);
        
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'HFplantarX_openOFM']).data = HFPlantar_lcl_av(1);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'HFplantarY_openOFM']).data = HFPlantar_lcl_av(2);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'HFplantarZ_openOFM']).data = HFPlantar_lcl_av(3);
        
        % create dynamic version of static marker
        PCA0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, PCA0_lcl_av);
        HFPlantar_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, HFPlantar_lcl_av);
        
        % add as virtual marker
        data.([side,'PCA']) = PCA0_dyn;
        data.([side,'HFPlantar']) = HFPlantar_dyn;
        
        %=======================================================================%
        %Tibia
        %=======================================================================%
        
        % extract markers from static trials
        ANK_sta = sdata.([side,'ANK']);
        MMA_sta = sdata.([side,'MMA']); % MMA marker only present in static trials
        HFB_sta = sdata.([side,'HFB']);
        SHN_sta = sdata.([side,'SHN']);
        TUB_sta = sdata.([side,'TUB']);
        
        % extract markers from dynamic trials
        ANK_dyn = data.([side,'ANK']);
        HFB_dyn = data.([side,'HFB']);
        SHN_dyn = data.([side,'SHN']);
        TUB_dyn = data.([side,'TUB']);
        
        % correct position of markers
        if settings.replace4 == true
            [ANK_sta,HFB_sta,~,SHN_sta] = replace4(ANK_sta,HFB_sta,TUB_sta,SHN_sta);
            [ANK_dyn,HFB_dyn,~,SHN_dyn] = replace4(ANK_dyn,HFB_dyn,TUB_dyn,SHN_dyn);
        end
        
        % create local coordinate systems 
        [O_sta, A_sta, L_sta, P_sta,~] = create_lcs(ANK_sta, HFB_sta-ANK_sta, SHN_sta-((ANK_sta+HFB_sta)/2),'xyz');
        [O_dyn, A_dyn, L_dyn, P_dyn,~] = create_lcs(ANK_dyn, HFB_dyn-ANK_dyn, SHN_dyn-((ANK_dyn+HFB_dyn)/2),'xyz');
        
        % create tibia virtual markers
        MMA0 = MMA_sta;
        
        % express RMMA_stat in lcs static
        MMA0_lcl = move_marker_gcs_2_lcs(O_sta, A_sta, L_sta, P_sta, MMA0);
        
        % round out errors and add to parameters
        MMA0_lcl_av = mean(MMA0_lcl);
        
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'MMAX_openOFM']).data = MMA0_lcl_av(1);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'MMAY_openOFM']).data = MMA0_lcl_av(2);
        data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.(['percent',side,'MMAZ_openOFM']).data = MMA0_lcl_av(3);
        
        % create dynamic version of static marker
        MMA0_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, MMA0_lcl_av);
        
        % add static marker to dynamic trial
        data.([side,'MMA']) = MMA0_dyn;
        
    end
end