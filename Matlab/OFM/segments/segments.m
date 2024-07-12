function [data, r, jnt] = segments(sdata, data, settings,version)

% DATA = MAKE_SEGMENTS(data,type,foot_flat) creates segment 'bones' 
% for use in kinematic / kinetic modelling. Bones are virtual markers 
% representing segment axes.
%
% ARGUMENTS
%
% data                 ... struct, trial data
% settings             ... struct, information to guide computational options
%                          settings.HJC: options PiG=chord function, Harrington
% 
%
% RETURNS
%  data                ... data with new 'bones' appended
%
% NOTES
% - Following anthropometric/metainfo data must be available:
%   'MarkerDiameter, R/LLegLength,R/LKneeWidth,R/LAnkleWidth 
%   Joint angles are unaffected
% - Only lower-limb bones are currently created
%

if nargin == 1
    error('add settings')
end

% Compute SACR marker position if 'RPSI', 'LPSI' is used -------------------------------------
if isfield(data,'RPSI')
    RPSI = data.RPSI;
    LPSI = data.LPSI;
    SACR = (RPSI+LPSI)/2;
    data.SACR = SACR;
end       

% Repeat for right and left sides
sides = {'R','L'};        
    for j = 1:length(sides)
        side = sides{j};

        if side == 'R'
            sign = 1;
        elseif side == 'L'
            sign = -1;
        end

        %=======================================================================%
        % Create tibia relative to the lab ( LabTibia)
        %=======================================================================%
        
        % Extract marker for the tibia relative to the lab
        ANK = data.([side,'ANK']);
        MMA = data.([side,'MMA']);
        TUB = data.([side,'TUB']);
        HFB = data.([side,'HFB']);
        SHN = data.([side,'SHN']);
        
        % Correct position of markers
        if version =="1.0"
            [ANK,HFB,TUB,~] = replace4(ANK,HFB,TUB,SHN);
        end

        % Create LabTibia origin
        LabTIB0 = (MMA+ANK)/2;
        
        % Project TUB onto the plane of MMA, ANK, HFB
        PROT = point_to_plane(TUB, MMA, ANK, HFB);

        % Create Vicon LabTibia axes
        if version == "1.0"
            [LabTIB0, LabTIB1, LabTIB2, LabTIB3, ~] = create_lcs(LabTIB0,PROT-LabTIB0,sign*(MMA-ANK),'zxy');
                    
        % Create 1.1 LabTibia axes
        elseif version=="1.1"
            [LabTIB0, LabTIB1, LabTIB2, LabTIB3, ~] = create_lcs(LabTIB0,PROT-LabTIB0,sign*(MMA-ANK),'yxz');
        end

        % if version=="1.0" && side=='R'
        %     tibia_axes_check(LabTIB0,LabTIB1,LabTIB2, LabTIB3, data)
        % end
        
        % Add as new channels
        data.([side,'LabTIB0']) = LabTIB0;
        data.([side,'LabTIB1']) = LabTIB1;
        data.([side,'LabTIB2']) = LabTIB2;
        data.([side,'LabTIB3']) = LabTIB3;

        %=======================================================================%
        % Create tibia segment with knee joint center
        %=======================================================================%
        % Extract some PiG markers ------------------------------------------------------------------
        
        KneeJC = data.([side,'KneeJC']);
        AnkleJC = data.([side,'AnkleJC']);
        TIR = data.([side,'TIR']);

        % Create Vicon tibia axes
        if version == "1.0"
            [TIB0, TIB1, TIB2, TIB3, ~] = create_lcs(AnkleJC,KneeJC-AnkleJC,sign*(AnkleJC-TIR),'zxy');
                
        
        % Create 1.1 tibia axes
        elseif version=="1.1"
            TIB0 = LabTIB0;
            TIB1 = LabTIB1;
            TIB2 = LabTIB2;
            TIB3 = LabTIB3;
        end


        % Add to struct
        data.([side,'TIB0']) = TIB0;
        data.([side,'TIB1']) = TIB1;
        data.([side,'TIB2']) = TIB2;
        data.([side,'TIB3']) = TIB3;
        
        
        %=======================================================================%
        % Create hindfoot segment
        %=======================================================================%
        
        % Extract markers
        PCA = data.([side,'PCA']);
        HEE = data.([side,'HEE']);
        STL = data.([side,'STL']);
        LCA = data.([side,'LCA']);
        CPG = data.([side,'CPG']);
        HFPlantar = data.([side,'HFPlantar']);
        
        % Correct position of markers
        if version =="1.0"
            [HEE,~,~,~] = replace4(HEE,LCA,STL,CPG);
        end

        % Create hindfoot axes
        if version == "1.0"
            [HDF0, HDF1, HDF2, HDF3] = create_lcs(HEE, HFPlantar - HEE,  PCA - HEE , 'zyx');

        % Create hindfoot axes
        elseif version =="1.1"
            [HDF0, HDF1, HDF2, HDF3] = create_lcs(HEE, HFPlantar - HEE,  PCA - HEE , 'xzy');
        end

        % Add as new channels
        data.([side,'HDF0']) = HDF0;
        data.([side,'HDF1']) = HDF1;
        data.([side,'HDF2']) = HDF2;
        data.([side,'HDF3']) = HDF3;

        
        %=======================================================================%
        % Create forefoot segment
        %=======================================================================%
        
        % Extract markers
        P1M = data.([side,'P1M']);
        P5M = data.([side,'P5M']);
        D1M = data.([side,'D1M']);
        D5M = data.([side,'D5M']);
        TOE = data.([side,'TOE']);
        D5M0 = data.([side,'D5M0']);
        
        % Correct position of markers
        if version =="1.0"
            [P1M,D5M0,TOE,P5M] = replace4(P1M,D5M0,TOE,P5M);
        end

        if settings.([side,'UseFloorFF']) == false
            D5M = D5M0;
        end
        
        % Create virtual markers
        projTOE = point_to_plane(TOE,D1M,D5M,P5M);
        projP1M = point_to_plane(P1M,D1M,D5M,P5M);
        
        P1P5dist = magnitude(projP1M-P5M);
        markerdiam = data.MetaInformation.Anthro.MarkerDiameter;
        proxFFscale = (P1P5dist - (markerdiam/2))./(2*P1P5dist);
        proxFF  = pointonline(projP1M,P5M,proxFFscale);

        %%% Find arch height
        % Extract virtual markers for the ArchHeightIndex (from
        % virtual_markers)
        P1Mlat = data.([side,'P1Mlat']);
        D1Mlat = data.([side,'D1Mlat']);
        D5Mlat = data.([side,'D5Mlat']);
        HEE_sta = sdata.([side,'HEE']);
        TOE_sta = sdata.([side,'TOE']);
        
        % Define Foot Length
        FootLength = mean(magnitude(HEE_sta-TOE_sta));
        
        % Calculate the ArchHeightIndex
        latprojP1M0lat = point_to_plane(P1Mlat,D1Mlat,D5Mlat,P5M);
        projP1M0lat = point_to_plane(P1Mlat,D1Mlat,D5M,P5M);
        ArchHeightIndex = magnitude(projP1M0lat-P1M)/FootLength*100;
        ArchHeight = [zeros(size(ArchHeightIndex)), zeros(size(ArchHeightIndex)), ArchHeightIndex(:,1)];

        % Create 1.0 forefoot axes
        if version =="1.0"
            [FOF0, FOF1, FOF2, FOF3] = create_lcs(projTOE, projTOE - proxFF,  sign*(D1M-D5M) , 'zxy');
        
        % Create 1.1 forefoot axes
        elseif version =="1.1"
            [FOF0, FOF1, FOF2, FOF3] = create_lcs(projTOE, projTOE - proxFF,  sign*(D1M-D5M) , 'xyz');
        end
%         if version=="1.0" && side=='R'
%             forefoot_axes_check(FOF1,FOF2,FOF3,projTOE,data)
%         end
        % 
        % Add as new channels
        data.([side,'FOF0']) = FOF0;
        data.([side,'FOF1']) = FOF1;
        data.([side,'FOF2']) = FOF2;
        data.([side,'FOF3']) = FOF3;
        data.([side,'ArchHeightIndex']) = ArchHeightIndex;
        data.([side,'ArchHeight']) = ArchHeight;
        
        %=======================================================================%
        % Create hallux segment
        %=======================================================================%
        
        % Extract markers     
        HLX = data.([side,'HLX']);
                
        % Create 1.0 hallux axes
        if version =="1.0"
            if side=='L'
                [HLX0, HLX1, HLX2, HLX3,~] = create_lcs(D1M, HLX-D1M,  D5M-D1M , 'zxy');
            else
                [HLX0, HLX1, HLX2, HLX3,~] = create_lcs(D1M, HLX-D1M,  D1M-D5M , 'zxy');
            end
        
        % Create 1.1 hallux axes
        elseif version == "1.1"
            if side=='L'
                [HLX0, HLX1, HLX2, HLX3,~] = create_lcs(D1M, HLX-D1M,  FOF0-FOF3 , 'yxz');
            else
                [HLX0, HLX1, HLX2, HLX3,~] = create_lcs(D1M, HLX-D1M,  FOF3-FOF0 , 'yxz');
            end
        end
        % if version=="1.0" && side=='R'
        %     hallux_axes_check(HLX0, HLX1, HLX2, HLX3, data)
        % end

        % Add as new channels
        data.([side,'HLX0']) = HLX0;
        data.([side,'HLX1']) = HLX1;
        data.([side,'HLX2']) = HLX2;
        data.([side,'HLX3']) = HLX3;             
    end


    [data, r, jnt] = get_bones(data);

end