function hallux_axes_check(O,axis1,axis2,axis3,data)

% HALLUX_AXES_CHECK(O,axis1,axis2,axis3,data) compares hallux 
% angles calculated from Vicon and openOFM
%
% ARGUMENTS
%   data       : struct. Dynamic trial data
%   O          : n x 3 array
%                Origin of the hallux segment
%   axis1      : n x 3 array
%                Proximal axis of the hallux segment
%   axis2      : n x 3 array
%                Lateral axis of the hallux segment (medial for right side)
%   axis3      : n x 3 array
%                Anterior axis of the hallux segment
%
% RETURNS
%   
%
% NOTES
% Also see hindfoot_axes_check, forefoot_axes_check, tibia_axes_check

% --- Extract markers ------------------------------

vicon_RHLX0 = data.RHLX0;
vicon_RHLX1 = data.RHLX1;
vicon_RHLX2 = data.RHLX2;
vicon_RHLX3 = data.RHLX3;

RHLX = data.RHLX;


% Add to segment origin
RHLX0 = RHLX;
RHLX1 = RHLX0 - 50*(axis1-O);
RHLX2 = RHLX0 + 50*(axis2-O);
RHLX3 = RHLX0 + 50*(axis3-O);

NRMSE_RHLX0 = nrmse(vicon_RHLX0,RHLX0)
NRMSE_RHLX1 = nrmse(vicon_RHLX1,RHLX1)
NRMSE_RHLX2 = nrmse(vicon_RHLX2,RHLX2)
NRMSE_RHLX3 = nrmse(vicon_RHLX3,RHLX3)



% -- Create/Plot vicon hallux axes (first frame) --------------------
figure
x = [vicon_RHLX0(1,1);vicon_RHLX1(1,1);vicon_RHLX2(1,1);vicon_RHLX3(1,1)];
y = [vicon_RHLX0(1,2);vicon_RHLX1(1,2);vicon_RHLX2(1,2);vicon_RHLX3(1,2)];
z = [vicon_RHLX0(1,3);vicon_RHLX1(1,3);vicon_RHLX2(1,3);vicon_RHLX3(1,3)];
names = {'vicon0','vicon1','vicon2','vicon3'};

plot3(x,y,z,'o', 'Color','r');
text(x,y,z,names,'HorizontalAlignment','right','VerticalAlignment','bottom','Color','r');
hold on 
O = vicon_RHLX0(1,:);
A = vicon_RHLX3(1,:) - O;
L = vicon_RHLX2(1,:) - O;
P = vicon_RHLX1(1,:) - O;
v = quiver3(O(1),O(2),O(3),A(1),A(2),A(3),'Color','r','DisplayName','Vicon');
quiver3(O(1),O(2),O(3),L(1),L(2),L(3),'Color','r');
quiver3(O(1),O(2),O(3),P(1),P(2),P(3),'Color','r');

% -- Create/Plot openOFM hallux axes (first frame) --------------------
x = [RHLX0(1,1);RHLX1(1,1);RHLX2(1,1);RHLX3(1,1)];
y = [RHLX0(1,2);RHLX1(1,2);RHLX2(1,2);RHLX3(1,2)];
z = [RHLX0(1,3);RHLX1(1,3);RHLX2(1,3);RHLX3(1,3)];
names = {'O','P','L','A'};
hold on
plot3(x,y,z,'d','Color','b')
text(x,y,z,names,'HorizontalAlignment','left','VerticalAlignment','top','Color','b');
hold on
O = RHLX0(1,:);
A_ofm = RHLX3(1,:) - O;
L_ofm = RHLX2(1,:) - O;
P_ofm = RHLX1(1,:) - O;
o = quiver3(O(1),O(2),O(3),A_ofm(1),A_ofm(2),A_ofm(3),'Color','b','DisplayName','openOFM');
quiver3(O(1),O(2),O(3),L_ofm(1),L_ofm(2),L_ofm(3),'Color','b');
quiver3(O(1),O(2),O(3),P_ofm(1),P_ofm(2),P_ofm(3),'Color','b');
legend([v,o])
title ('Hallux axes check')
grid on
box on

% % compare angles and add to plot?
% a = angle(A, A_ofm, 'deg');
% p = angle(P, P_ofm, 'deg');
% l = angle(L, L_ofm, 'deg');
% 
% annotation('textbox', [0.7, 0.3, 0.1, 0.1], 'String', ['3 diff = ', num2str(a) ' deg'])
% annotation('textbox', [0.7, 0.4, 0.1, 0.1], 'String', ['2 diff = ', num2str(l) ' deg'])
% annotation('textbox', [0.7, 0.5, 0.1, 0.1], 'String', ['1 diff = ', num2str(p) ' deg'])
