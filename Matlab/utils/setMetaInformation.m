function MetaInfo = setMetaInformation(fl)

% MetaInfo = SETZOOSYSTEM(fl) creates 'MetaInfo' branch for data
% being imported to biomechZoo
%
% ARGUMENTS
%  data      ... Zoo data
%  r         ... Parameters (struct)
%
% RETURNS
%  data      ... Zoo data with appropriate parameters loaded


% Set defaults
%
zch = {'Analog','Anthro','AVR','CompInfo','SourceFile','Units','Version','Video'};


% Set up struc
%
MetaInfo = struct;
for i = 1:length(zch)
    MetaInfo.(zch{i}) = struct;
end

section = {'Video','Analog'};

for i = 1:length(section)
    MetaInfo.(section{i}).Channels = {};
    MetaInfo.(section{i}).Freq = [];
    MetaInfo.(section{i}).Indx = [];
    MetaInfo.(section{i}).ORIGINAL_START_FRAME = [];
    MetaInfo.(section{i}).ORIGINAL_END_FRAME   = [];
    MetaInfo.(section{i}).CURRENT_START_FRAME  = [];
    MetaInfo.(section{i}).CURRENT_END_FRAME    = []; 
end

MetaInfo.Processing = '';
MetaInfo.SourceFile = char(fl);
 
MetaInfo.Units.Markers = 'mm';
MetaInfo.Units.Angles = 'deg';
MetaInfo.Units.Scalars = 'mm';

% 
