% openOFM_process : script to demonstrate functionality of processing of
% a sample data from OGL lab

clear

%% STEP 0: Initialize version and setttings for analysis
% set version
version = '1.1';
settings.manualAnthro = false;   % if true, anthropometric values are manually set in section 2.2

%% STEP 1: Get data
% Get files
r = which('openOFM_process.m');
indx = strfind(r, filesep);
subject_fld = [r(1:indx(end-1)), 'Data_Sample', filesep, 'Sample'];

%% STEP 2: Compute ofm
% 2.1 - Load data
fl_subject_static = [subject_fld, filesep, 'static.c3d'];
fl_subject_dynamic = [subject_fld, filesep, 'dynamic.c3d'];

sdata = load_markers_c3d(fl_subject_static);
data = load_markers_c3d(fl_subject_dynamic);

% 2.2 Extract relevant Vicon settings
% These settings can be manually set to "true" or "false" here
settings.LHindFootFlat = sdata.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.LHindFootFlat.data;
settings.RHindFootFlat = sdata.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.RHindFootFlat.data;
settings.RUseFloorFF = sdata.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.RUseFloorFF.data;
settings.LUseFloorFF = sdata.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.LUseFloorFF.data;

% 2.2 - Set anthropometric values manually
if settings.manualAnthro == true
    warning('Manually inputted anthropmetric values are being used.')
    data.MetaInformation.Anthro.MarkerDiameter = 1;
    data.MetaInformation.Anthro.InterAsisDistance = 1;
    data.MetaInformation.Anthro.RLegLength = 1;
    data.MetaInformation.Anthro.LLegLength = 1;
    data.MetaInformation.Anthro.RKneeWidth = 1;
    data.MetaInformation.Anthro.LKneeWidth = 1;
    data.MetaInformation.Anthro.RAnkleWidth = 1;
    data.MetaInformation.Anthro.LAnkleWidth = 1;
    data.MetaInformation.Anthro.RThighRotation = 0;
    data.MetaInformation.Anthro.LThighRotation = 0;
    data.MetaInformation.Anthro.RShankRotation = 0;
    data.MetaInformation.Anthro.LShankRotation = 0;
end


% 2.3 - Compute hip, knee and PiG ankle joint center
data = hipjointcentrePiG(data);
data = kneejointcenterPiG(data);
data = anklejointcenterPiG(data);

% 2.4 - run openOFM
data_openOFM = openOFM(sdata, data, settings, version);

% 3 - Compare angles
%plot title
plot_title = [' LHFF(',num2str(settings.LHindFootFlat),') RHFF(', num2str(settings.RHindFootFlat), ...
    ') LUseFloor (', num2str(settings.LUseFloorFF),') RUseFloor (', num2str(settings.RUseFloorFF), ')'];                                    % info in title

plot_angles_process(data_openOFM,plot_title)

