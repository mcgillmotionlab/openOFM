function data = openOFM(sdata, data, settings,version)

% OPENFOOT computes multi-segment foot model parameters
%
% ARGUMENTS
%   sdata      ... struct, containing cleaned data from static trial 
%   data       ... struct, containing cleaned data from dynamic trial 
%   settings   ... struct, Controls model calculations, see struct options below
%
% RETURNS
%   data      ...  struct, containing parameters computed by openfoot


% 1 - create dynamic version of virtual markers present in static trial + compute phi and omega
data = virtual_markers(data, sdata, settings, version);

% 2 - create virtual segment embedded axes
[data, r, jnt] = segments(sdata, data, settings,version);

% 3 - Compute joint angles according to Grood and Suntay method
[~,dir] = getDir(data);
KIN = get_grood_suntay(r, jnt, dir, version);

% 4 - Update reference system to match OFM and add to data struct
data = refsystem(data, KIN, version);

