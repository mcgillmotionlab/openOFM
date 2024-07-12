function r = prep_bones(data, bone)

dimOFM = {'0','1','2','3'};
% 0 is origin of bone (zero)
% 1 corresponds to x
% 2 corresponds to y
% 3 corresponds to z

if isempty(bone)
   error('OFM virtual bones required for kinematics calculation')
else
    
    for i = 1:length(bone(:,1))
        d = cell(1,length(dimOFM));
        
        if strcmp(bone{i,1},'GLB')
            d{1} =  zeros(size(data.([bone{i+1,1},dimOFM{1}])));
            d{2} =  [d{1}(:,1)+10 d{1}(:,2:3)];
            d{3} =  [d{1}(:,1) d{1}(:,2)+10 d{1}(:,3)];
            d{4} =  [d{1}(:,1:2) d{1}(:,3)+10];
        else
            for j = 1:4
                d{j} = data.([bone{i,1},dimOFM{j}]);
            end
        end
        bn = bone{i,2};
        ort = getdataOFM(d);
        r.(bn).ort = ort;
    end
    
end


