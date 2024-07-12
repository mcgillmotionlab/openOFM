function [data,bone, jnt] = get_bones(data)

% [data,bone, jnt] = GET_boneS_DATA(data) retrieves bone information from data struct and creates
% joints. This is used for grood and suntay calculations 
%
% ARGUMENTS
% data    ....  struct containing marker data
%
% RETURNS
% bone   ....   The names of the different segment bones
% jnt    ...    The joint name and the bones used to calculate the joint
%               angle ex. RightMTP joint is calculated from RightForeFoot and RightHallux


% Revision History
%
% Updated Dec 2010 by Philippe C. Dixon
% - more simple code
% - used for both OFM and PG models
%
% Updated April 2016 by Philippe C. Dixon
% - Removed backwards Matlab compatibility 
%
% Updated June 2017 by Philippe C. Dixon
% - upperbody bones head and thorax tested

bone = [];
jnt = [];

% Add on to improve agreement with vicon
%
if ~isfield(data,'RTIB0') 
    error('no ankle joint centre virtual marker available')
end

if ~isfield(data,'RLabTIB0') 
    error('no ankle joint centre virtual marker available for tibia relative to lab')
end

ch = fieldnames(data);

%---Oxford Foot Model joints and bones---
%Tibia relative to lab
if ismember('RLabTIB0',ch)
    [~,indx]=ismember({'RLabTIB0'},ch);
    chname = ch{indx};

    bplate = {chname(1:7),'RightTibiaLab'};
    bone = [bone;bplate];
end
%Tibia relative to the lab
if ismember({'RLabTIB0'},ch)       
    jplate = {'RightTibiaLab','Global','RightTibiaLab'};
    bplate = {'GLB','Global'};     
    
    jnt=[jnt;jplate];
    bone = [bone;bplate];
end

if ismember({'RTIB0','RHDF0'},ch)   
    [~,indx]=ismember({'RTIB0'},ch);
    chname = ch{indx};
    
    jplate = {'RightAnkleOFM','RightTibiaOFM','RightHindFoot'};
    bplate = {chname(1:4),'RightTibiaOFM'};  
    
    jnt=[jnt;jplate];
    bone = [bone;bplate];
end
% tibia and ff
if ismember({'RTIB0','RFOF0'},ch)  
    [~,indx]=ismember({'RTIB0'},ch);
    chname = ch{indx};
    
    jplate = {'RightFFTBA','RightTibiaOFM','RightForeFoot'};
    bplate = {chname(1:4),'RightTibiaOFM'};   
        
    jnt=[jnt;jplate];    
    bone = [bone;bplate];
end

if ismember({'RHDF0','RFOF0'},ch)  
    [~,indx]=ismember({'RHDF0'},ch);
    chname = ch{indx};
    
    jplate = {'RightMidFoot','RightHindFoot','RightForeFoot'};
    bplate = {chname(1:4),'RightHindFoot'};   
        
    jnt=[jnt;jplate];    
    bone = [bone;bplate];
end

if ismember({'RFOF0','RHLX0'},ch)
    [~,indx]=ismember({'RFOF0'},ch);
    chname = ch{indx};

    jplate = {'RightMTP','RightForeFoot','RightHallux'};
    bplate = {chname(1:4),'RightForeFoot'};

    jnt=[jnt;jplate];
    bone = [bone;bplate];
end

if ismember('RHLX0',ch)
    [~,indx]=ismember({'RHLX0'},ch);
    chname = ch{indx};

    bplate = {chname(1:4),'RightHallux'};
    bone = [bone;bplate];
end

if ismember({'LTIB0','LHDF0'},ch)
    [~,indx]=ismember({'LTIB0'},ch);
    chname = ch{indx};

    jplate = {'LeftAnkleOFM','LeftTibiaOFM','LeftHindFoot'};
    bplate = {chname(1:4),'LeftTibiaOFM'};

    jnt=[jnt;jplate];
    bone = [bone;bplate];
end
%Tibia relative to lab
if ismember({'LLabTIB0'},ch)   
    [~,indx]=ismember({'LLabTIB0'},ch);
    chname = ch{indx};
    
    jplate = {'LeftTibiaLab','Global','LeftTibiaLab'};
    bplate = {'GLB','Global'};  
    
    jnt=[jnt;jplate];
    bone = [bone;bplate];
end
if ismember('LLabTIB0',ch)
    [~,indx]=ismember({'LLabTIB0'},ch);
    chname = ch{indx};

    bplate = {chname(1:7),'LeftTibiaLab'};
    bone = [bone;bplate];
end

% tibia and ff
if ismember({'LTIB0','LFOF0'},ch)  
    [~,indx]=ismember({'LTIB0'},ch);
    chname = ch{indx};
    
    jplate = {'LeftFFTBA','LeftTibiaOFM','LeftForeFoot'};
    bplate = {chname(1:4),'LeftTibiaOFM'};   
        
    jnt=[jnt;jplate];    
    bone = [bone;bplate];
end

if ismember({'LHDF0','LFOF0'},ch)
    [~,indx]=ismember({'LHDF0'},ch);
    chname = ch{indx};

    jplate = {'LeftMidFoot','LeftHindFoot','LeftForeFoot'};
    bplate = {chname(1:4),'LeftHindFoot'};

    jnt=[jnt;jplate];
    bone = [bone;bplate];
end

if ismember({'LFOF0','LHLX0'},ch)
    [~,indx]=ismember({'LFOF0'},ch);
    chname = ch{indx};

    jplate = {'LeftMTP','LeftForeFoot','LeftHallux'};
    bplate = {chname(1:4),'LeftForeFoot'};

    jnt=[jnt;jplate];
    bone = [bone;bplate];
end

if ismember('LHLX0',ch)
    [~,indx]=ismember({'LHLX0'},ch);
    chname = ch{indx};

    bplate = {chname(1:4),'LeftHallux'};
    bone = [bone;bplate];
end

bone = prep_bones(data, bone);
