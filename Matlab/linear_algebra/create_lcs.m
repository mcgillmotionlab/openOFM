function [O, lcs1, lcs2, lcs3, axes_system] = create_lcs(O, vec1, vec2, order)

% [O, lcs1, lcs2, lcs3, axes_system] = CREATE_LCS(O, vec1, vec2, order)
% creates a local coordinate system.
%
% ARGUMENTS
%   O            ... n x 3 array: origin of the local coordinate system
%   vec1         ... n x 3 array: vector representing the first axis
%   vec2         ... n x 3 array: second vector used to create the axes
%   order        ... order in which the axes will be created 'xyz', 'xzy',
%                 'zxy'or none
%
% RETURNS
%   O            ... n x 3 array: origin of the local coordinate system
%   lcs1         ... n x 3 array: marker on the first axis of the local coordinate system
%   lcs2         ... n x 3 array: marker on the second axis of the local coordinate system
%   lcs3         ... n x 3 array: marker on the third axis of the local coordinate system
%   axes_system  ... axes system composed of the 3 axes created
%
%
if nargin == 3
    axis1 = makeunit(vec1);
    axis2 = makeunit(cross(vec2,axis1));
    axis3 = makeunit(cross(axis1,axis2));

    lcs1 = O + axis1;
    lcs2 = O + axis2;
    lcs3 = O + axis3;

    axes_system = [axis1; axis2; axis3];
end

if nargin == 4
switch order
    case 'xyz'
%         more recent code, not sure whether its worth updating
%         mag1 = norm(vec1);
%         axis1 = vec1/mag1;
%         mag2 = norm(cross(axis1,vec2));
%         axis2 = (cross(axis1,vec2))/mag2;
%         mag3 = norm(cross(axis1,axis2));
%         axis3 = (cross(axis1,axis2))/mag3;

        axis1 = makeunit(vec1);                 % x - forward
        axis2 = makeunit(cross(axis1,vec2));    % y - up
        axis3 = makeunit(cross(axis1,axis2));   % z - lateral for right

        lcs1 = O + axis1;
        lcs2 = O + axis2;
        lcs3 = O + axis3;

    case 'xzy'
        axis1 = makeunit(vec1);                 % x - forward
        axis3 = makeunit(cross(axis1,vec2));    % z - lateral for right
        axis2 = makeunit(cross(axis3,axis1));   % y - up

        lcs1 = O + axis1;
        lcs2 = O + axis2;
        lcs3 = O + axis3;

    case 'zxy'
        axis3 = makeunit(vec1);                % z - anterior
        axis1 = makeunit(cross(vec2,axis3));   % x - proximal
        axis2 = makeunit(cross(axis3,axis1));  % y - medial for right

        lcs1 = O + axis1;
        lcs2 = O + axis2;
        lcs3 = O + axis3;

    case 'zyx'
        axis3 = makeunit(vec1);                % z - forward
        axis2 = makeunit(cross(vec2,axis3));   % y - medial for right
        axis1 = makeunit(cross(axis2,axis3));  % x - down

        lcs1 = O + axis1;
        lcs2 = O + axis2;
        lcs3 = O + axis3;


    case 'yzx'
        axis2 = makeunit(vec1);                % y - up
        axis3 = makeunit(cross(axis2,vec2));   % z - lateral for right
        axis1 = makeunit(cross(axis2,axis3));  % x - forward

        lcs1 = O + axis1;
        lcs2 = O + axis2;
        lcs3 = O + axis3;

    case 'yxz'
        axis2 = makeunit(vec1);                % y - up
        axis1 = makeunit(cross(vec2,axis2));   % x - forward
        axis3 = makeunit(cross(axis1,axis2));  % z - lateral for right

        lcs1 = O + axis1;
        lcs2 = O + axis2;
        lcs3 = O + axis3;

end
axes_system = [axis1; axis2; axis3];
end
