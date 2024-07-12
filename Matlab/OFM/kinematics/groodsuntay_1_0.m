function [alpha,beta,gamma] = groodsuntay_1_0(r,jnt,dir)
%
% [alpha,beta,gamma] = GROODSUNTAY(r,jnt,dir)
% Arguments
%   r    ...  struct with ref system of each segment
%   j    ...  1 x 3 cell array {joint_name, proximal/global segment, distal segment}
%   dir  ...  global gait direction (used to correct pelvis asind(dots)
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
% - Grood and Suntay angle calculations based on adaptation by Vaughan 'The
%   Gait Book' Appendix B, p95. 
% - Offsets chosen to match oxford foot model outputs
% - Axis set-up follows Vicon

% Updated January 15th 2011
% - works with VICON2GROODSUNTAY

%---SET UP VARIABLES ---


pbone = jnt{2};
dbone = jnt{3};

pax = r.(pbone).ort;  % stores xyz local axes for each frame
dax = r.(dbone).ort;

if strfind(pbone,'Right')
    bone = pbone(6:end);
elseif strfind(pbone,'Left')
    bone = pbone(5:end);
else
    bone = pbone;
end

% dir only needed for global

if nargin == 2 && strcmp(bone, 'Global')
    error('missing dir for global angles')
end

if nargin < 3
    dir = false;
end


%---CREATE AXES FOR GROOD AND SUNTAY CALCULATIONS----
switch bone
case 'Global'
        [~,~,prox_x,dist_x,prox_y,~,~,dist_z] = makeax(pax,dax);
             
         % jneg is base case (no correction)
         % J needs to be checked
         if strcmp(dir, 'Jneg')
             alpha = -asind(dot(prox_y,dist_z,2));   %checked
             beta = -asind(dot(dist_z, prox_x,2));
             gamma  = asind(dot(dist_x,prox_x,2));
         elseif strcmp(dir, 'Jpos')
             alpha = asind(dot(prox_y,dist_z,2));   %checked
             beta = asind(dot(dist_z, prox_x,2));
             gamma  = -asind(dot(dist_x,prox_x,2));       
         elseif strcmp(dir, 'Ineg')
             beta = asind(dot(prox_y,dist_z,2));
             alpha = -asind(dot(dist_z, prox_x,2));
             gamma  = -asind(dot(dist_x,prox_y,2));
         elseif strcmp(dir, 'Ipos')
             beta = -asind(dot(prox_y,dist_z,2));   %to be checked
             alpha = asind(dot(dist_z, prox_x,2));
             gamma  = asind(dot(dist_x,prox_y,2));
         else
             error(['unknown direction : ', dir])
         end                
    case 'TibiaOFM'    % hindfoot and forefoot tibia angle

        [floatax,prox_x,~,prox_y,dist_y,~,dist_z] = makeax_1_0(pax,dax);

        alpha = asind(dot(floatax,prox_x,2));        % plantar/ dorsi
        beta  = asind(dot(prox_y,dist_z,2));         % int / ext
        gamma = -asind(dot(floatax,dist_y,2));       % inv / eve

    case {'HindFoot','ForeFoot'}   % hind/forefoot and forefoot/hallux angle

        [floatax,~,~,prox_y,dist_y,prox_z,dist_z] = makeax_1_0(pax,dax);

        alpha = asind(dot(floatax,prox_z,2));       % plantar / dorsi
        beta = asind(dot(prox_y,dist_z,2));         % abd / add
        gamma  = -asind(dot(floatax,dist_y,2));     % sup / pro

end



