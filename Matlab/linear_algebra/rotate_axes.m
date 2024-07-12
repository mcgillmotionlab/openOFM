function rot_axes = rotate_axes(axes,theta,axis)

% rot_axes = ROTATE_AXES(axes,theta,axis) will rotate the axes about one
% axis from the local coordinate system. 
%
% ARGUMENTS
%   axes      ... axes to rotate
%   theta     ... angle of rotation
%   axis      ... axis from the local coordinate system to rotate about:
%                 'x', 'y' or 'z'
%
% RETURNS
%   rot_axes  ... axes rotated about an axis from the local coordinate
%                 system
% 

switch axis
    case 'x'
        axis = axes(1,:);
        
    case 'y'
        axis = axes(2,:);
        
    case 'z'
        axis = axes(3,:);
end

% Compute axis variables
L = magnitude(axis);
a = axis(1);
b = axis(2);
c = axis(3);
V = sqrt(b^2 + c^2);

% Rotate about the Global x-axis
rot_x =    [1    0     0; 
            0   c/V  b/V; 
            0  -b/V  c/V];
        
% Rotate about the Global y-axis
rot_y =    [V/L  0    a/L;
             0   1     0;
           -a/L  0    V/L];
         
% Rotate about the Global z-axis
rot_z =  [cosd(theta)  sind(theta) 0;
         -sind(theta)  cosd(theta) 0;
              0         0          1];
          
% Reverse the rotation about the y-axis
rev_rot_y = [V/L 0  -a/L;
             0   1    0;
            a/L  0   V/L];
         
% Reverse the rotation about the x-axis
rev_rot_x =  [1   0      0;
              0  c/V   -b/V;
              0  b/V    c/V];
          
   
% Create transformation matrix
t = rot_x* rot_y* rot_z* rev_rot_y* rev_rot_x;

% Rotate axes
rot_axes = axes*t;

end
