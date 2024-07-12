function data = kneejointcenterPiG(data)


% Compute joint offsets for knee and ankle
KneeWidth = (data.MetaInformation.Anthro.RKneeWidth + data.MetaInformation.Anthro.LKneeWidth)/2;
KneeOffset = (KneeWidth + data.MetaInformation.Anthro.MarkerDiameter)/2;

% Repeat for right and left sides
sides = {'R','L'};        
    for j = 1:length(sides)
        side = sides{j};

            % Extract some PiG markers ------------------------------------------------------------------
            KNE = data.([side,'KNE']);    
            
            % Compute knee joint centre --------------------------------------------
            % computation based on pyCGM.py's interpretatin of PiG 'chord function'

            % Extract openfoot hip joint centers
            HipJC = data.([side,'HipJC']);
 
            %=======================================================================%
            % Create femur segment
            %=======================================================================%

            % Extract marker and value for femur rotation
            
            THI = data.([side,'THI']);
            
            VCMThighOffset = data.MetaInformation.Anthro.([side,'ThighRotation']);
    
            % Calculate the femur rotation given a thigh offset
            if VCMThighOffset ~= 0
                FemurRotation = zeros(size(HipJC,1),1);
                for i = 1:size(HipJC,1)
                    [~,~,~,~,Taxes] = create_lcs(HipJC(i,:),KNE(i,:)-HipJC(i,:),THI(i,:)-KNE(i,:),'yxz');
                    THI_lcl_Taxes = ctransform(gunit,Taxes,THI(i,:)-HipJC(i,:));
                    wy = THI_lcl_Taxes (2);
                    wz = -THI_lcl_Taxes(3);
                    thi = asin(KneeOffset/magnitude(HipJC(i,:)-KNE(i,:)));
                    psi = VCMThighOffset;
                    
                    a  = wz*wz;
                    b  = 2*cos(psi)*sin(psi)*sin(thi)*wz*wy;
                    c  = sin(psi)*sin(psi)*(sin(thi)*sin(thi)*wy*wy-cos(thi)*cos(thi)*wz*wz);
                    
                    thetaplus  = asin((-b+sqrt(b*b-4*a*c))/(2*a));
                    thetaminus = asin((-b-sqrt(b*b-4*a*c))/(2*a));
                    
                    if thetaplus*VCMThighOffset > 0
                        FemurRotation(i,:) = -thetaminus;
                    else
                        FemurRotation(i,:) = -thetaplus;
                    end
                end
            else
                FemurRotation = zeros(size(HipJC,1),1);
                
            end
            FemurRotation = mean(FemurRotation);
            
            % Correct thigh wand marker
            THI_lcl_Thigh = zeros(size(THI));
            THR = zeros(size(THI));
            for i = 1:size(THI,1)
                [~, ~, ~, ~, Thigh] = create_lcs(KNE(i,:),HipJC(i,:)-KNE(i,:),-THI(i,:),'yxz');
                THI_lcl_Thigh(i,:) = ctransform(gunit, Thigh, THI(i,:)-KNE(i,:));
                if side=='L'
                    rot_axes = rotate_axes(Thigh,rad2deg(-FemurRotation),'y');
                else
                    rot_axes = rotate_axes(Thigh,rad2deg(FemurRotation),'y');
                end
                THR_vec_gbl = ctransform(rot_axes, gunit, THI_lcl_Thigh(i,:));
                THR(i,:) = THR_vec_gbl + KNE(i,:);
            end
            
            % Create knee joint center based on corrected wand marker
            KneeJC = chordPiG(THR,HipJC,KNE,KneeOffset);
            data.([side,'KneeJC']) = KneeJC;

    end