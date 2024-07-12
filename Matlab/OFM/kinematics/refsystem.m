function [data, r] = refsystem(data, KIN,version)
% Change names to match vicon nomenclature

r = struct;
if version == "1.0"
    % 'RightTibiaLab'   % Tibia relative to Lab
    r.RightTibiaLab.PlaDor = KIN.RightTibiaLab.alpha;
    r.RightTibiaLab.IntExt = KIN.RightTibiaLab.gamma;
    r.RightTibiaLab.InvEve = KIN.RightTibiaLab.beta;
    
    % 'LeftTibiaLab'   % Tibia relative to Lab
    r.LeftTibiaLab.PlaDor = KIN.LeftTibiaLab.alpha;
    r.LeftTibiaLab.IntExt = -KIN.LeftTibiaLab.gamma;
    r.LeftTibiaLab.InvEve = -KIN.LeftTibiaLab.beta;
        
    %Right Ankle (HindFoot relative to Tibia)
    r.RightAnkleOFM.PlaDor = KIN.RightAnkleOFM.alpha;
    r.RightAnkleOFM.InvEve = KIN.RightAnkleOFM.gamma;     % vicon int/ext is the same as IDA beta/Add (
    r.RightAnkleOFM.IntExt = KIN.RightAnkleOFM.beta;
    
    % 'LeftAnkleOFM'   % HindFoot relative to Tibia
    r.LeftAnkleOFM.PlaDor = KIN.LeftAnkleOFM.alpha;
    r.LeftAnkleOFM.InvEve = -KIN.LeftAnkleOFM.gamma;     % vicon int/ext is the same as IDA beta/Add (
    r.LeftAnkleOFM.IntExt = -KIN.LeftAnkleOFM.beta;

    % 'RightFFTBA'     %Forefoot relative to Tibia
    r.RightFFTBA.PlaDor = KIN.RightFFTBA.alpha;
    r.RightFFTBA.InvEve = KIN.RightFFTBA.gamma;
    r.RightFFTBA.IntExt = KIN.RightFFTBA.beta;
    
    % 'LeftFFTBA'      %Forefoot relative to Tibia
    r.LeftFFTBA.PlaDor = KIN.LeftFFTBA.alpha;
    r.LeftFFTBA.InvEve = -KIN.LeftFFTBA.gamma;
    r.LeftFFTBA.IntExt = -KIN.LeftFFTBA.beta;
    
    %'RightMidFoot'   % Forefoot relative to Hindfoot
    r.RightMidFoot.PlaDor = KIN.RightMidFoot.alpha;
    r.RightMidFoot.SupPro = KIN.RightMidFoot.gamma;
    r.RightMidFoot.AbdAdd = KIN.RightMidFoot.beta;
    
    % 'LeftMidFoot'   % Forefoot relative to Hindfoot
    r.LeftMidFoot.PlaDor = KIN.LeftMidFoot.alpha;
    r.LeftMidFoot.SupPro = -KIN.LeftMidFoot.gamma;
    r.LeftMidFoot.AbdAdd = -KIN.LeftMidFoot.beta;
    
    % 'RightMTP'       % Hallux relative to Forefoot
    r.RightMTP.PlaDor = KIN.RightMTP.alpha;
    r.RightMTP.AbdAdd = KIN.RightMTP.beta;
    r.RightMTP.IntExt = zeros(size(KIN.RightMTP.gamma));   % garbage
    
    % 'LeftMTP'          % Hallux relative to Forefoot
    r.LeftMTP.PlaDor = KIN.LeftMTP.alpha;
    r.LeftMTP.AbdAdd = -KIN.LeftMTP.beta;
    r.LeftMTP.IntExt = zeros(size(KIN.LeftMTP.gamma));     % garbage

elseif version == "1.1"

    % 'RightTibiaLab'   % Tibia relative to Lab
    r.RightTibiaLab.PlaDor = KIN.RightTibiaLab.alpha;
    r.RightTibiaLab.IntExt = KIN.RightTibiaLab.gamma;
    r.RightTibiaLab.InvEve = KIN.RightTibiaLab.beta;
    
    % 'LeftTibiaLab'   % Tibia relative to Lab
    r.LeftTibiaLab.PlaDor = KIN.LeftTibiaLab.alpha;
    r.LeftTibiaLab.IntExt = -KIN.LeftTibiaLab.gamma;
    r.LeftTibiaLab.InvEve = -KIN.LeftTibiaLab.beta;
        
    %Right Ankle (HindFoot relative to Tibia)
    r.RightAnkleOFM.PlaDor = KIN.RightAnkleOFM.alpha;
    r.RightAnkleOFM.InvEve = KIN.RightAnkleOFM.gamma;     % vicon int/ext is the same as IDA beta/Add (
    r.RightAnkleOFM.IntExt = KIN.RightAnkleOFM.beta-90;
    
    % 'LeftAnkleOFM'   % HindFoot relative to Tibia
    r.LeftAnkleOFM.PlaDor = KIN.LeftAnkleOFM.alpha;
    r.LeftAnkleOFM.InvEve = -KIN.LeftAnkleOFM.gamma;     % vicon int/ext is the same as IDA beta/Add (
    r.LeftAnkleOFM.IntExt = -KIN.LeftAnkleOFM.beta+90;
    
    % 'RightFFTBA'     %Forefoot relative to Tibia
    r.RightFFTBA.PlaDor = KIN.RightFFTBA.alpha;
    r.RightFFTBA.InvEve = KIN.RightFFTBA.gamma;
    r.RightFFTBA.IntExt = KIN.RightFFTBA.beta-90;
    
    % 'LeftFFTBA'      %Forefoot relative to Tibia
    r.LeftFFTBA.PlaDor = KIN.LeftFFTBA.alpha;
    r.LeftFFTBA.InvEve = -KIN.LeftFFTBA.gamma;
    r.LeftFFTBA.IntExt = -KIN.LeftFFTBA.beta+90;
    
    %'RightMidFoot'   % Forefoot relative to Hindfoot
    r.RightMidFoot.PlaDor = KIN.RightMidFoot.alpha;
    r.RightMidFoot.SupPro = KIN.RightMidFoot.gamma;
    r.RightMidFoot.AbdAdd = KIN.RightMidFoot.beta-90;
    
    % 'LeftMidFoot'   % Forefoot relative to Hindfoot
    r.LeftMidFoot.PlaDor = KIN.LeftMidFoot.alpha;
    r.LeftMidFoot.SupPro = -KIN.LeftMidFoot.gamma;
    r.LeftMidFoot.AbdAdd = -KIN.LeftMidFoot.beta+90;
    
    % 'RightMTP'       % Hallux relative to Forefoot
    r.RightMTP.PlaDor = KIN.RightMTP.alpha;
    r.RightMTP.AbdAdd = -KIN.RightMTP.gamma;
    r.RightMTP.IntExt = zeros(size(KIN.RightMTP.beta));   % garbage
    
    % 'LeftMTP'          % Hallux relative to Forefoot
    r.LeftMTP.PlaDor = KIN.LeftMTP.alpha;
    r.LeftMTP.AbdAdd = KIN.LeftMTP.gamma;
    r.LeftMTP.IntExt = zeros(size(KIN.LeftMTP.beta));     % garbage
end
    
    % add to data struct
    data = addchannelsgs(data, r);



