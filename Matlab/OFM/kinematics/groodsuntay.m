function [alpha,beta,gamma] = groodsuntay(r,jnt,dir)
%
% [alpha,beta,gamma] = GROODSUNTAY(r,jnt,dir)
% Arguments
%   r    ...  struct with ref system of each segment
%   j    ...  1 x 3 cell array {joint_name, proximal/global segment, distal segment}
%   dir  ...  global gait direction (used to correct global tibia asind(dots)
%
% Returns
%  Global tibia, and hindfoot/forefoot tibia angles
%   alpha  ...   n x 1 flexion angle
%   beta  ...   n x 1 abduction angle
%   gamma   ...   n x 1 rotation angle
%  Hindfoot forefootm, forefoot hallux angles
%   alpha  ...   n x 1 flexion angle
%   beta  ...   n x 1 rotation angle
%   gamma   ...   n x 1 abduction angle
%
% NOTES:
% - Grood and Suntay angle calculations based on original description of the OFM by Carson et al. (2001)
% - Offsets chosen to match oxford foot model outputs
% - Axis set-up based on Wu et al. (2002) ISB recommendation on definition
% of joint coordinate syste of various joints for the reporting of human
% joint motion - part I

% Updated January 15th 2011
% - works with VICON2GROODSUNTAY

%---SET UP VARIABLES ---


pbone = jnt{2};
dbone = jnt{3};

pax = r.(pbone).ort;  % stores xyz local axes for each frame
dax = r.(dbone).ort;

if strfind(pbone,'Right')
    prox_bone = pbone(6:end);
elseif strfind(pbone,'Left')
    prox_bone = pbone(5:end);
else
    prox_bone = pbone;
end

% dir only needed for global

if nargin == 2 && strcmp(prox_bone, 'Global')
    error('missing dir for global angles')
end

if nargin < 3
    dir = false;
end


%---CREATE AXES FOR GROOD AND SUNTAY CALCULATIONS----
[floatax,~, prox_x,dist_x,prox_y,dist_y,prox_z,dist_z] = makeax(pax,dax);
switch prox_bone
case 'Global'
             
         % jneg is base case (no correction)
         % J needs to be checked
         if strcmp(dir, 'Jneg')
             alpha = -asind(dot(prox_y,dist_y,2));   %checked
             beta = -asind(dot(dist_y, prox_x,2));
             gamma  = asind(dot(dist_x,prox_x,2));
         elseif strcmp(dir, 'Jpos')
             alpha = asind(dot(prox_y,dist_y,2));   %checked
             beta = asind(dot(dist_y, prox_x,2));
             gamma  = -asind(dot(dist_x,prox_x,2));       
         elseif strcmp(dir, 'Ineg')
             beta = asind(dot(prox_y,dist_y,2));
             alpha = -asind(dot(dist_y, prox_x,2));
             gamma  = -asind(dot(dist_x,prox_y,2));
         elseif strcmp(dir, 'Ipos')
             beta = -asind(dot(prox_y,dist_y,2));   %to be checked
             alpha = asind(dot(dist_y, prox_x,2));
             gamma  = asind(dot(dist_x,prox_y,2));
         else
             error(['unknown direction : ', dir])
         end

    case 'ForeFoot' %Forefoot / hallux
        alpha = -asind(dot(floatax,prox_y,2));         % plantar/dorsi
        beta = acosd(dot(prox_z,dist_x,2));           % rotation
        gamma  = -asind(dot(floatax,dist_z,2));        % abduction

    otherwise   
        alpha = -asind(dot(floatax,prox_x,2));         % plantar/dorsi
        beta = acosd(dot(prox_z,dist_x,2));           % abduction or rotation
        gamma  = -asind(dot(floatax,dist_z,2));        % abduction or rotation

end

