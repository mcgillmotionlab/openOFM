% openOFM_validate: Demonstrate processing of raw data to replicate Vicon
% processed data, stored in the "Data" folder

clear

% set version
version = '1.0';

% Get files
r = which('openOFM_validate.m');
indx = strfind(r, filesep);
fld = [r(1:indx(end-1)), 'Data_Validate'];

files = dir(fld); % Get a list of all files and folders in this folder.
dirFlags = [files.isdir]; % Get a logical vector that tells which is a directory.
subDirs = files(dirFlags); % Extract only those that are directories.
subjects = {subDirs(3:end).name}; % Get only the folder names into a cell array.

for s = 1:length(subjects)
    subject = subjects{s};
    subj_fld = [fld, filesep, subject];

    fl_static_raw = [subj_fld, filesep, 'static.c3d'];
    fl_static_processed = [subj_fld, filesep, 'static_processed.c3d'];
    fl_dynamic_raw = [subj_fld, filesep, 'dynamic.c3d'];
    fl_dynamic_processed = [subj_fld, filesep, 'dynamic_processed.c3d'];

    % load data
    sdata_raw = load_markers_c3d(fl_static_raw);
    sdata_processed = load_markers_c3d(fl_static_processed);
    data_raw = load_markers_c3d(fl_dynamic_raw);
    data_processed = load_markers_c3d(fl_dynamic_processed);

    % extract settings
    settings = get_settings(sdata_processed);

    % Fetch hip, knee and PiG ankle joint center
    data_raw = hipjointcentrePiG(data_raw);
    data_raw = kneejointcenterPiG(data_raw);
    data_raw = anklejointcenterPiG(data_raw);

    % run open foot
    data_openOFM = openOFM(sdata_raw, data_raw, settings,version);

    % compare angles
    plot_title = [subject,' LHFF(',num2str(settings.LHindFootFlat),') RHFF(', num2str(settings.RHindFootFlat), ...
        ') LUseFloor (', num2str(settings.LUseFloorFF),') RUseFloor (', num2str(settings.RUseFloorFF), ')'];                                    % info in title

    plot_angles(data_openOFM,data_processed,plot_title)

    % compare metrics (arch height)
    RArchHeightIndexNRMSE = nrmse(data_processed.RArchHeightIndex(:,3),data_openOFM.RArchHeightIndex);
    LArchHeightIndexNRMSE = nrmse(data_processed.LArchHeightIndex(:,3),data_openOFM.LArchHeightIndex);
    RArchHeightNRMSE = nrmse(data_processed.RArchHeight(:,3),data_openOFM.RArchHeight);
    LArchHeightNRMSE = nrmse(data_processed.LArchHeight(:,3),data_openOFM.LArchHeight);
end


