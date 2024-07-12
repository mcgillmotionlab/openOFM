function tibia_axes_check(O_RTibia,axis1,axis2, axis3, v_data)

% TIBIA_AXES_CHECK(O_RTibia,A_RTibia,L_RTibia, P_RTibia, data) compares tibia 
% angles calculated from Vicon and openOFM
%
% ARGUMENTS
%   data       : struct. Dynamic trial data
%   O_RTibia   : n x 3 array
%                Origin of the tibia segment
%   A_RTibia   : n x 3 array
%                Anterior axis of the tibia segment
%   L_RTibia   : n x 3 array
%                Lateral axis of the tibia segment (medial for right side)
%   P_RTibia   : n x 3 array
%                Proximal axis of the tibia segment
%
% RETURNS
%   
%
% NOTES
% Also see hindfoot_axes_check, forefoot_axes_check, hallux_axes_check
% 

% --- Extract markers ------------------------------
% RMMA = v_data.RMMA;
% RANK = v_data.RANK;
% RHFB = v_data.RHFB;
% RTUB = v_data.RTUB;
% RSHN = v_data.RSHN;
% vicon_RTIB0 = O_RTibia_vicon;
% vicon_RTIB1 = (A_RTibia_vicon-O_RTibia_vicon)*50+O_RTibia_vicon;
% vicon_RTIB2 = (L_RTibia_vicon-O_RTibia_vicon)*50+O_RTibia_vicon;
% vicon_RTIB3 = (P_RTibia_vicon-O_RTibia_vicon)*50+O_RTibia_vicon;
% [RANK,RHFB,RTUB,RSHN] = replace4(RANK,RHFB,RTUB,RSHN);
% midmal = (RMMA+RANK)/2 % = data.RAJC;
vicon_RTIB0 = O_RTibia;
vicon_RTIB1 = v_data.RTIB1;
vicon_RTIB2 = v_data.RTIB2;
vicon_RTIB3 = v_data.RTIB3;  % see bodybuilder code line 557, this axis is multiply by 400 instead of 50
vicon_RTIB3 = vicon_RTIB0+((vicon_RTIB3 - vicon_RTIB0)/8);
% vicon_axes = [vicon_RTIB1-vicon_RTIB0; vicon_RTIB2-vicon_RTIB0; vicon_RTIB3-vicon_RTIB0];
%RTIB0 = O_RTibia;
%O_RTibia = midmal;
RTIB0 = O_RTibia;

  RTIBx = (axis1-O_RTibia)*50+O_RTibia;
  RTIBy = (axis2-O_RTibia)*50+O_RTibia;
  RTIBz = (axis3-O_RTibia)*50+O_RTibia;
%   RTIB1 = (A_RTibia-O_RTibia)
%   RTIB2 = (L_RTibia-O_RTibia)
%   RTIB3 = (P_RTibia-O_RTibia);
%   RTIB0T = RTibia
%   RTIB1 = ctransform(RTibia,vicon_axes,RTIB1);
%   RTIB1 = RTIB1+vicon_RTIB0;
%   RTIB2 = ctransform(RTibia,vicon_axes,RTIB2);
%   RTIB2 = RTIB2+vicon_RTIB0;
%   RTIB3 = ctransform(RTibia,vicon_axes,RTIB3);
%   RTIB3 = RTIB3+vicon_RTIB0;
  
diff= vicon_RTIB0 - RTIB0
NRMSE_RTIB0 = nrmse(vicon_RTIB0,RTIB0)
NRMSE_RTIB1 = nrmse(vicon_RTIB1,RTIBx)
NRMSE_RTIB2 = nrmse(vicon_RTIB2,RTIBy)
NRMSE_RTIB3 = nrmse(vicon_RTIB3,RTIBz)

% -- Create/Plot vicon forefoot axes (first frame) --------------------
figure
x = [vicon_RTIB0(1,1);vicon_RTIB1(1,1);vicon_RTIB2(1,1);vicon_RTIB3(1,1)];
y = [vicon_RTIB0(1,2);vicon_RTIB1(1,2);vicon_RTIB2(1,2);vicon_RTIB3(1,2)];
z = [vicon_RTIB0(1,3);vicon_RTIB1(1,3);vicon_RTIB2(1,3);vicon_RTIB3(1,3)];
names = {'vicon0','viconX','viconY','viconZ'};

plot3(x,y,z,'o', 'Color','r');
text(x,y,z,names,'HorizontalAlignment','right','VerticalAlignment','bottom','Color','r');
hold on 
O = vicon_RTIB0(1,:);
X = vicon_RTIB1(1,:) - O;
Y = vicon_RTIB2(1,:) - O;
Z = vicon_RTIB3(1,:) - O;
v = quiver3(O(1),O(2),O(3),X(1),X(2),X(3),'Color','r','DisplayName','Vicon');
quiver3(O(1),O(2),O(3),Y(1),Y(2),Y(3),'Color','r');
quiver3(O(1),O(2),O(3),Z(1),Z(2),Z(3),'Color','r');

% -- Create/Plot openOFM forefoot axes (first frame) --------------------
x = [RTIB0(1,1);RTIBx(1,1);RTIBy(1,1);RTIBz(1,1)];
y = [RTIB0(1,2);RTIBx(1,2);RTIBy(1,2);RTIBz(1,2)];
z = [RTIB0(1,3);RTIBx(1,3);RTIBy(1,3);RTIBz(1,3)];
names = {'O','X','Y','Z'};
hold on
plot3(x,y,z,'d','Color','b')
text(x,y,z,names,'HorizontalAlignment','left','VerticalAlignment','top','Color','b');
hold on
O = RTIB0(1,:);
X_ofm = RTIBx(1,:) - O;
Y_ofm = RTIBy(1,:) - O;
Z_ofm = RTIBz(1,:) - O;
o = quiver3(O(1),O(2),O(3),X_ofm(1),X_ofm(2),X_ofm(3),'Color','b','DisplayName','openOFM');
quiver3(O(1),O(2),O(3),Y_ofm(1),Y_ofm(2),Y_ofm(3),'Color','b');
quiver3(O(1),O(2),O(3),Z_ofm(1),Z_ofm(2),Z_ofm(3),'Color','b');
legend([v,o])
title ('Tibia axes check')
grid on
box on

% compare angles and add to plot?
% a = angle(X, X_ofm, 'deg');
% p = angle(Z, Y_ofm, 'deg');
% l = angle(Y, Z_ofm, 'deg');
% 
% annotation('textbox', [0.7, 0.3, 0.1, 0.1], 'String', ['3 diff = ', num2str(a) ' deg'])
% annotation('textbox', [0.7, 0.4, 0.1, 0.1], 'String', ['2 diff = ', num2str(l) ' deg'])
% annotation('textbox', [0.7, 0.5, 0.1, 0.1], 'String', ['1 diff = ', num2str(p) ' deg'])
end
