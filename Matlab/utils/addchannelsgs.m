function data = addchannelsgs(data,KIN,ERR)

if nargin == 2
    ERR = [];
end

%-- add static angles
if isfield(KIN,'RightAnkleStatic')
    kch = {'RightAnkleStatic','LeftAnkleStatic'};
    
    for i = 1:length(kch)
        
        dsub = {'x','y','z'};
        asub = {'PlaDor','InvEve','IntExt'};
        
        for j = 1:length(dsub)
            data.([kch{i},'Angle_',dsub{j}]) = KIN.(kch{i}).(asub{j});
            
            if ~isempty(ERR)
                data.([kch{i},'Angle_',dsub{j}]).event.NRMSE = [1 NaN 0]; % no error possible
            end
        end
    end
    
end

if isfield(KIN,'RightAnkleOFM')
    
    sides = {'Right','Left'};
    
    for i = 1:length(sides)
        
        side = sides{i};
        
        data.([side,'HFTBA_x']) = KIN.([side,'AnkleOFM']).PlaDor;
        data.([side,'HFTBA_y']) = KIN.([side,'AnkleOFM']).InvEve;
        data.([side,'HFTBA_z']) = KIN.([side,'AnkleOFM']).IntExt;
       
        data.([side,'FFHFA_x']) = KIN.([side,'MidFoot']).PlaDor;
        data.([side,'FFHFA_y']) = KIN.([side,'MidFoot']).AbdAdd;
        data.([side,'FFHFA_z']) = KIN.([side,'MidFoot']).SupPro;
        
        data.([side,'HXFFA_x']) = KIN.([side,'MTP']).PlaDor;
        data.([side,'HXFFA_y']) = KIN.([side,'MTP']).AbdAdd;
        
        if isfield(KIN, 'RightTibiaLab')
            data.([side,'TIBA_x']) = KIN.([side,'TibiaLab']).PlaDor;  %TibiaLab
            data.([side,'TIBA_y']) = KIN.([side,'TibiaLab']).InvEve;
            data.([side,'TIBA_z']) = KIN.([side,'TibiaLab']).IntExt;
            data.([side,'FFTBA_x']) = KIN.([side,'FFTBA']).PlaDor;
            data.([side,'FFTBA_y']) = KIN.([side,'FFTBA']).InvEve;
            data.([side,'FFTBA_z']) = KIN.([side,'FFTBA']).IntExt;
        end
        
        if ~isempty(ERR)
            
            if isfield(ERR, [side, 'AnkleOFM'])
                if isfield   (KIN, 'RightTibiaLab')
                    data.([side,'TIBA_x']).event.NRMSE = [1 ERR.([side,'TibiaLab']).PlaDor.NRMSE 0];
                    data.([side,'TIBA_y']).event.NRMSE = [1 ERR.([side,'TibiaLab']).InvEve.NRMSE 0];
                    data.([side,'TIBA_z']).event.NRMSE = [1 ERR.([side,'TibiaLab']).IntExt.NRMSE 0];
                end
                data.([side,'HFTBA_x']).event.NRMSE = [1 ERR.([side,'AnkleOFM']).PlaDor.NRMSE 0];
                data.([side,'HFTBA_y']).event.NRMSE = [1 ERR.([side,'AnkleOFM']).InvEve.NRMSE 0];
                data.([side,'HFTBA_z']).event.NRMSE = [1 ERR.([side,'AnkleOFM']).IntExt.NRMSE 0];
                
                data.([side,'FFTBA_x']).event.NRMSE = [1 ERR.([side,'FFTBA']).PlaDor.NRMSE 0];
                data.([side,'FFTBA_y']).event.NRMSE = [1 ERR.([side,'FFTBA']).InvEve.NRMSE 0];
                data.([side,'FFTBA_z']).event.NRMSE = [1 ERR.([side,'FFTBA']).IntExt.NRMSE 0];
                
                data.([side,'FFHFA_x']).event.NRMSE = [1 ERR.([side,'MidFoot']).PlaDor.NRMSE 0];
                data.([side,'FFHFA_z']).event.NRMSE = [1 ERR.([side,'MidFoot']).AbdAdd.NRMSE 0];
                data.([side,'FFHFA_y']).event.NRMSE = [1 ERR.([side,'MidFoot']).SupPro.NRMSE 0];
                
                data.([side,'HXFFA_x']).event.NRMSE = [1 ERR.([side,'MTP']).PlaDor.NRMSE 0];
                data.([side,'HXFFA_y']).event.NRMSE = [1 ERR.([side,'MTP']).AbdAdd.NRMSE 0];
                data.([side,'HXFFA_z']).event.NRMSE = [1 ERR.([side,'MTP']).IntExt.NRMSE 0];
            end
            
        end
        
    end
end


