function data = error_data(data,settings,KIN)

% data = ERROR_DATA(data,settings) computes global and lower-limb
% joint angles based on the joint coordinate system of Grood and Suntay (1983)
%
% ARGUMENTS
%  data     ...  raw data
%  settings ...  Settings control (struct) with the following fields:
%                'graph' (boolean). Graph comparisons against Vicon. Default, false
%                'comp'  (boolean). Vicon vs BiomeZoo RMS diff (if available). Default, true
%
% RETURNS
%  data    ...   raw data appended with kinematic channels
%
%
% NOTES:
% - It is anatomically implausible for the vectors to flip during walking but may be
%   possible for tasks with large ranges of motion (e.g. running). A correction has been
%   implemented at the knee, but might require future updates (see 'checkflippg')
% - For PiG, choice of axes for angle computation based on work of Vaughan
%   (Dynamics of Human Gait 1999, Appendix B p94-96). This is the Grood and Suntay method.
% - For OFM, choice of axes based on trial and error.
% - Lower limb PiG outputs of this function have been validated
%   (see Fig4.dpf and Supplemental Fig2.pdf in ~\biomechZoo-samplestudy\Figures\manuscript\
% - Head angles are not offset by static posture (PiG angles use static offset)
%
% SUMMARY OF CALCULATIONS
%


% Revision History
%
% Created by Philippe C Dixon and JJ Loh 2008
%
% Updated by Philippe C Dixon January 2011
% - tested against vicon output 100% match for both PIG and OFM
% - grood and suntay calculations occur in embedded function 'groodsuntay'
%
% Updated by Philippe C Dixon September 2012
% - possibility to graph results as a visual check
% - added abd/add of hallux segment
% - added simple demo mode
% - calculations simplified
% - only reference frame is Vicon
% - correction for axis flipping at the knee implemented using 'checkflip' function
%
% Updated by Philippe C Dixon June 2016
% - Function can run using 'raw' files, i.e. data with PiG markers only, not run
%   through Vicon modeller (see makebones.m). This functionality has not been extended
%   to the OFM data
% - Static trial is used to correctly adjust ankle offset values
% - Foot flat option matches option in Vicon
%
% Updated by Philippe C. Dixon Sept 2016
% - biomechZoo pelvis angles validated against PiG outputs for straight
%   walking see ~/biomechZoo-samplestudy/Figures/Pelvis_kinematics_Straight.pdf
% - improved graphical outputs
%
% Updated by Philippe C. Dixon June 2017
% - global head and thorax angles included
% - More testing of global angles in all directions
% - Fixed bug with graphing outputs
%
% Updated by Philippe C. Dixn Dec 2017
% - Bug fix for axis flipping for large ROM movement at the hip and knee
%   based on 'atan2' approach from pyCGM (see pyCGM.py --> getangle). For
%   more info see: Schwartz and Dixon "The Effect of Subject Measurement Error on
%   Joint Kinematics in the Conventional Gait Model: Insights From the Open-source \
%   pyCGM tool using High Performance Computing Methods". Plos One, In
%   press. Update for ankle and pelvis should be considered
% - Bug fix for static trials with less than 3 frames ('length' changed to
%  'size') when building ort in 'getdataPiG' sub function


% Set defaults
%

if ~isfield(settings, 'graph')
    settings.graph = false;
    settings.comp = false;
end

if nargin==1
    settings.graph = false;
    settings.comp  = false;
end


%---- CHECK ACCURACY OF CALCULATIONS AGAINST ORIGINAL VICON DATA (DISPLAY OPTIONAL) ----
%
if settings.comp == true
    ERR=checkvicon(KIN,data);
    if isempty(fieldnames(ERR))
        ERR = [];
    end
else
    ERR = [];
end

%---- ADD COMPUTED ANGLES TO DATA STRUCT -----------------------------------------------
%
data = addchannelsgs(data,KIN,ERR);

%=================EMBEDDED FUNCTIONS===========================================

function ERR=checkvicon(KIN,data)

ERR = struct;
chOFM = [];

if isfield(data,'RHFTBA')
    [errOFM,chOFM]= checkOFM(KIN,data);
end

for j = 1:length(chOFM)
    ERR.(chOFM{j}) = errOFM.(chOFM{j});
end


function [ERR,ch] = checkOFM(KIN,data)

RA = zeros(3,1);
RMF = zeros(3,1);
RMTP = zeros(3,1);
RTL = zeros(3,1);
RFT = zeros(3,1);

LA = zeros(3,1);
LMF = zeros(3,1);
LMTP = zeros(3,1);
LTL = zeros(3,1);
LFT = zeros(3,1);

subch = {'PlaDor','InvEve','IntExt'}; % Ankle angle
for k = 1:length(subch)
    RA(k) = nrmse(data.RHFTBA(:,k),KIN.RightAnkleOFM.(subch{k}));
    LA(k) = nrmse(data.LHFTBA(:,k),KIN.LeftAnkleOFM.(subch{k}));
end

subch = {'PlaDor','AbdAdd','SupPro'};  % MidFoot angle
for k = 1:length(subch)
    RMF(k) = nrmse(data.RFFHFA(:,k), KIN.RightMidFoot.(subch{k}));
    LMF(k) = nrmse(data.LFFHFA(:,k), KIN.LeftMidFoot.(subch{k}));
end

subch = {'PlaDor','AbdAdd','IntExt'};  % MTP angle,'IntExt' not yet supported
for k = 1:length(subch)
    RMTP(k) = nrmse(data.RHXFFA(:,k), KIN.RightMTP.(subch{k}));
    LMTP(k) = nrmse(data.LHXFFA(:,k), KIN.LeftMTP.(subch{k}));
end
if isfield   (KIN, 'RightTibiaLab')
    subch = {'PlaDor','InvEve','IntExt'}; % TibiaLab angle
    for k = 1:length(subch)
        RTL(k) = nrmse(data.RTIBA(:,k),KIN.RightTibiaLab.(subch{k}));
        LTL(k) = nrmse(data.LTIBA(:,k),KIN.LeftTibiaLab.(subch{k}));
    end
    
    subch = {'PlaDor','InvEve','IntExt'};  % FFTBA angle
    for k = 1:length(subch)
        RFT(k) = nrmse(data.RFFTBA(:,k), KIN.RightFFTBA.(subch{k}));
        LFT(k) = nrmse(data.LFFTBA(:,k), KIN.LeftFFTBA.(subch{k}));
    end
end
ERR.RightAnkleOFM.PlaDor.NRMSE =RA(1);
ERR.RightAnkleOFM.InvEve.NRMSE =RA(2);
ERR.RightAnkleOFM.IntExt.NRMSE =RA(3);

ERR.RightMidFoot.PlaDor.NRMSE = RMF(1);
ERR.RightMidFoot.SupPro.NRMSE = RMF(2);
ERR.RightMidFoot.AbdAdd.NRMSE = RMF(3);

ERR.RightMTP.PlaDor.NRMSE = RMTP(1);
ERR.RightMTP.AbdAdd.NRMSE = RMTP(2);
ERR.RightMTP.IntExt.NRMSE = 0;  % garbage

ERR.RightTibiaLab.PlaDor.NRMSE =RTL(1);  %TibiaLab
ERR.RightTibiaLab.InvEve.NRMSE =RTL(2);
ERR.RightTibiaLab.IntExt.NRMSE =RTL(3);

ERR.RightFFTBA.PlaDor.NRMSE =RFT(1);  %FFTBA
ERR.RightFFTBA.InvEve.NRMSE =RFT(2);
ERR.RightFFTBA.IntExt.NRMSE =RFT(3);


ERR.LeftAnkleOFM.PlaDor.NRMSE = LA(1);
ERR.LeftAnkleOFM.InvEve.NRMSE = LA(2);
ERR.LeftAnkleOFM.IntExt.NRMSE = LA(3);

ERR.LeftMidFoot.PlaDor.NRMSE = LMF(1);
ERR.LeftMidFoot.SupPro.NRMSE = LMF(2);
ERR.LeftMidFoot.AbdAdd.NRMSE = LMF(3);

ERR.LeftMTP.PlaDor.NRMSE = LMTP(1);
ERR.LeftMTP.AbdAdd.NRMSE = LMTP(2);
ERR.LeftMTP.IntExt.NRMSE = 0;  % garbage

ERR.LeftTibiaLab.PlaDor.NRMSE =LTL(1);  %TibiaLab
ERR.LeftTibiaLab.InvEve.NRMSE =LTL(2);
ERR.LeftTibiaLab.IntExt.NRMSE =LTL(3);

ERR.LeftFFTBA.PlaDor.NRMSE =LFT(1);  %FFTBA
ERR.LeftFFTBA.InvEve.NRMSE =LFT(2);
ERR.LeftFFTBA.IntExt.NRMSE =LFT(3);

ch = fieldnames(ERR);




