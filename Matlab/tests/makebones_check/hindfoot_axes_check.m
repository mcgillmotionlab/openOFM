function hindfoot_axes_check(O,axis1, axis2, axis3,data)

% HINDFOOT_AXES_CHECK(O,axis1, axis2, axis3,data) compares hindfoot 
% angles calculated from Vicon and openOFM
%
% ARGUMENTS
%   data       : struct. Dynamic trial data
%   O          : n x 3 array
%                Origin of the hindfoot segment
%   axis1      : n x 3 array
%                Proximal axis of the hindfoot segment
%   axis2      : n x 3 array
%                Lateral axis of the hindfoot segment (medial for right side)
%   axis3      : n x 3 array
%                Anterior axis of the hindfoot segment
%
% RETURNS
%   
%
% NOTES
% Also see tibia_axes_check, forefoot_axes_check, hallux_axes_check
% --- Extract markers ------------------------------

vicon_RHDF0 = data.RHDF0;
vicon_RHDF1 = data.RHDF1;
vicon_RHDF2 = data.RHDF2;
vicon_RHDF3 = data.RHDF3;

RHDF0 = O;
RHDF1 = (axis1-O)*50 + O;
RHDF2 = (axis2-O)*50 + O;
RHDF3 = (axis3-O)*50 + O;

NRMSE_RHDF0 = nrmse(vicon_RHDF0,RHDF0)
NRMSE_RHDF1 = nrmse(vicon_RHDF1,RHDF1)
NRMSE_RHDF2 = nrmse(vicon_RHDF2,RHDF2)
NRMSE_RHDF3 = nrmse(vicon_RHDF3,RHDF3)

% -- Create/Plot vicon forefoot axes (first frame) --------------------
figure
x = [vicon_RHDF0(1,1);vicon_RHDF1(1,1);vicon_RHDF2(1,1);vicon_RHDF3(1,1)];
y = [vicon_RHDF0(1,2);vicon_RHDF1(1,2);vicon_RHDF2(1,2);vicon_RHDF3(1,2)];
z = [vicon_RHDF0(1,3);vicon_RHDF1(1,3);vicon_RHDF2(1,3);vicon_RHDF3(1,3)];
names = {'vicon0','vicon1','vicon2','vicon3'};

plot3(x,y,z,'o', 'Color','r');
text(x,y,z,names,'HorizontalAlignment','right','VerticalAlignment','bottom','Color','r');
hold on 
O = vicon_RHDF0(1,:);
A = vicon_RHDF3(1,:) - O;
L = vicon_RHDF2(1,:) - O;
P = vicon_RHDF1(1,:) - O;
v = quiver3(O(1),O(2),O(3),A(1),A(2),A(3),'Color','r','DisplayName','Vicon');
quiver3(O(1),O(2),O(3),L(1),L(2),L(3),'Color','r');
quiver3(O(1),O(2),O(3),P(1),P(2),P(3),'Color','r');

% -- Create/Plot openOFM forefoot axes (first frame) --------------------
x = [RHDF0(1,1);RHDF1(1,1);RHDF2(1,1);RHDF3(1,1)];
y = [RHDF0(1,2);RHDF1(1,2);RHDF2(1,2);RHDF3(1,2)];
z = [RHDF0(1,3);RHDF1(1,3);RHDF2(1,3);RHDF3(1,3)];
names = {'O','P','L','A'};
hold on
plot3(x,y,z,'d','Color','b')
text(x,y,z,names,'HorizontalAlignment','left','VerticalAlignment','top','Color','b');
hold on
O = RHDF0(1,:);
A_ofm = RHDF3(1,:) - O;
L_ofm = RHDF2(1,:) - O;
P_ofm = RHDF1(1,:) - O;
o = quiver3(O(1),O(2),O(3),A_ofm(1),A_ofm(2),A_ofm(3),'Color','b','DisplayName','openOFM');
quiver3(O(1),O(2),O(3),L_ofm(1),L_ofm(2),L_ofm(3),'Color','b');
quiver3(O(1),O(2),O(3),P_ofm(1),P_ofm(2),P_ofm(3),'Color','b');
legend([v,o])
title ('Hindfoot axes check')
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
end