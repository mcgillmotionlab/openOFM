function [data] = anklejointcenterPiG(data)


% Compute joint offsets and ankle
AnkleWidth = (data.MetaInformation.Anthro.RAnkleWidth + data.MetaInformation.Anthro.LAnkleWidth)/2;
AnkleOffset = (AnkleWidth + data.MetaInformation.Anthro.MarkerDiameter)/2;

% Repeat for right and left sides
sides = {'R','L'};        
    for j = 1:length(sides)
        side = sides{j};            
            %=======================================================================%
            % Create tibia segment
            %=======================================================================%
            
            % Extract value for shank offset and knee joint center
            ShankOffset = data.MetaInformation.Anthro.([side,'ShankRotation']);
            KneeJC = data.([side,'KneeJC']);
            TIB = data.([side,'TIB']);
            ANK = data.([side,'ANK']);

            % Calculate tibia rotation
            if ShankOffset ~= 0
                TibiaRotation = zeros(size(KneeJC,1),1);
                for i = 1:size(KneeJC,1)
                    [~,~,~,~,Taxes] = create_lcs(KneeJC(i,:),ANK(i,:)-KneeJC(i,:),TIB(i,:)-ANK(i,:),'yxz');
                    TIB_lcl_Taxes = ctransform(gunit,Taxes,TIB(i,:)-KneeJC(i,:));
                    
                    vy = TIB_lcl_Taxes(2);
                    vz = -TIB_lcl_Taxes(3);
                    thi = asin(AnkleOffset/magnitude(KneeJC(i,:)-ANK(i,:)));
                    psi = ShankOffset;
                    
                    a  = vz*vz;
                    b  = 2*cos(psi)*sin(psi)*sin(thi)*vy*vz;
                    c  = sin(psi)*sin(psi)*(sin(thi)*sin(thi)*vy*vy-cos(thi)*cos(thi)*vz*vz);
                    
                    thetaplus  = asin((-b+sqrt(b*b-4*a*c))/(2*a));
                    thetaminus = asin((-b-sqrt(b*b-4*a*c))/(2*a));
                    
                    if thetaplus*ShankOffset > 0
                        TibiaRotation(i,:) = -thetaminus;
                    else
                        TibiaRotation(i,:) = -thetaplus;
                    end
                    
                end
                
            else
                TibiaRotation = zeros(size(KneeJC,1),1);
            end
            TibiaRotation = mean(TibiaRotation);
            
            % Correct TIB marker
            TIB_lcl_Shank = zeros(size(TIB));
            TIR = zeros(size(TIB));
            for i = 1:size(KneeJC,1)
                [~, ~, ~, ~, Shank] = create_lcs(ANK(i,:),KneeJC(i,:)-ANK(i,:),TIB(i,:)-ANK(i,:),'yxz');
                TIB_lcl_Shank(i,:) = ctransform(gunit, Shank, TIB(i,:)-ANK(i,:));
                if side=='L'
                    rot_axes = rotate_axes(Shank,rad2deg(-TibiaRotation),'y');
                else
                    rot_axes = rotate_axes(Shank,rad2deg(TibiaRotation),'y');
                end
                TIR_vec_gbl = ctransform(rot_axes, gunit, TIB_lcl_Shank(i,:));
                TIR(i,:) = TIR_vec_gbl + ANK(i,:);
            end
            data.([side,'TIR']) = TIR;
            
            % Create ankle joint center marker
            AnkleJC = chordPiG(TIR,KneeJC,ANK,AnkleOffset);
            data.([side,'AnkleJC']) = AnkleJC;

    end
end

