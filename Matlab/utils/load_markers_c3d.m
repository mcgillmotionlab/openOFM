function data = load_markers_c3d(fl)

% data = loadc3d(fld,del) Converts .c3d files to .zoo format
%
% ARGUMENTS
%  fl   ...  full path to individual file (string).
%
% RETURNS
%  data  ...  zoo data. Return if fld is individual file (mostly used by 'director')
%
% See also csv2zoo, readc3d
%
% NOTES:
% - The function attempts to fix invalid fielnames via the makevalidfield.m function



% SET DEFAULTS / ERROR CHECK -----------------------------------------------------------------
%
tic                                                                          % start timer


% Extract info from c3d file
%
r = readc3d(fl);

% Initialize zoo data structure
%
data = struct;
data.MetaInformation = setMetaInformation(fl);

% Add video channels to data struct
%
vfld = fieldnames(r.VideoData);
vlbl = cell(size(vfld));

for v = 1:length(vfld)
    vlbl{v} = makevalidfield(r.VideoData.(vfld{v}).label);                 % fixes invalid fieldnames
    
    if isfield(data,vlbl{v})
        vlbl{v} = [vlbl{v},num2str(v)];
    end
    
    temp = [makecolumn(r.VideoData.(vfld{v}).xdata),makecolumn(r.VideoData.(vfld{v}).ydata),...
        makecolumn(r.VideoData.(vfld{v}).zdata)];
    data.(vlbl{v}) = temp;
end


% Set frequency information
%
data.MetaInformation.Freq = r.Header.VideoHZ;


% set header information
%
data.MetaInformation.Header = setHeader(r);

% Set unit information
%
data.MetaInformation.Units = setUnits(r,data);


% set anthro metainformation (if available) to MetaInformation branch of data struct
%
data.MetaInformation.Anthro = setAnthro(r);


% set all other meta info
%
mch = setdiff(fieldnames(r),{'VideoData','AnalogData'});

for m = 1:length(mch)
    data.MetaInformation.OtherMetaInfo.(mch{m}) = r.(mch{m});
end



%---SHOW END OF PROGRAM-------------------------------------------------------------------------
disp(['Finished loading data for ', fl, ' in ', num2str(toc), ' sec'])


function Header = setHeader(r)

Header = struct;

if isfield(r.Parameter,'SUBJECTS')
    Header.SubName =  deblank(makerow(r.Parameter.SUBJECTS.NAMES.data));
else
    Header.SubName = '';
end
Header.Date = '';
Header.Time = '';
Header.Description = '';  % this remains empty


function Units = setUnits(r,data)

pch = fieldnames(r.Parameter.POINT);

Units = struct;
for j = 1:length(pch)
    
    if strfind(pch{j},'UNITS')
        Units.(pch{j}) = makerow(r.Parameter.POINT.(pch{j}).data);
    end
end

if isfield(Units,'POWER_UNITS')
    Units.Power = 'W/kg'; % Vicon is lying r.Parameter.POINT.POWER_UNITS is W/kg not W
end

ach = data.MetaInformation.Analog.Channels;
check = true;
count = 1;
while check && count < length(ach)
    if strfind(ach{count},'Voltage')
        Units.EMG = 'Voltage';
        check = false;
    else
        count = count+1;
    end
end


function Anthro = setAnthro(r)

if isfield(r.Parameter,'PROCESSING')
    ach = setdiff(fieldnames(r.Parameter.PROCESSING),{'id','islock'});
    
    for j = 1:length(ach)
        rr = r.Parameter.PROCESSING.(ach{j});
        
        if isstruct(rr)
            rr = rr.data;
        end
        
        Anthro.(ach{j}) =  rr;
    end
    
else
    Anthro = struct;
end