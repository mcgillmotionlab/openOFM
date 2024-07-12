function check_tib_dyn_axes (O_dyn, A_dyn, L_dyn, P_dyn, data)

% CHECK_TIB_DYN_AXES(O_dyn, A_dyn, L_dyn, P_dyn, data) compares openOFM's 
% tibia technical axes for dynamic trials with Vicon's axes. 
%
% ARGUMENTS
%   data    ... struct. Dynamic trial data
%   O_dyn   ... n x 3 array
%               Origin of the tibia segment
%   A_dyn   ... n x 3 array
%               Anterior axis of the tibia segment
%   L_dyn   ... n x 3 array
%               Lateral axis of the tibia segment (medial for right side)
%   P_dyn   ... n x 3 array
%               Proximal axis of the tibia segment
%
% RETURNS
%   
%
% NOTES
% Also see check_tib_stat_axes


A_dyn = (A_dyn-O_dyn)*50+O_dyn;
L_dyn = (L_dyn-O_dyn)*50+O_dyn;
P_dyn = (P_dyn-O_dyn)*50+O_dyn;


DRTIB0 = data.DRTIB0.line;
DRTIB1 = data.DRTIB1.line;
DRTIB2 = data.DRTIB2.line;
DRTIB3 = data.DRTIB3.line;

% check normalized root mean square
NRMSE_DRTIB0_dyn = nrmse(O_dyn,DRTIB0)
NRMSE_DRTIB1_dyn = nrmse(A_dyn,DRTIB1)
NRMSE_DRTIB2_dyn = nrmse(L_dyn,DRTIB2)
NRMSE_DRTIB3_dyn = nrmse(P_dyn,DRTIB3)
    
% -- Create/Plot vicon dummy axes (first frame) --------------------
figure
x = [DRTIB0(1,1);DRTIB3(1,1);DRTIB2(1,1);DRTIB1(1,1)];
y = [DRTIB0(1,2);DRTIB3(1,2);DRTIB2(1,2);DRTIB1(1,2)];
z = [DRTIB0(1,3);DRTIB3(1,3);DRTIB2(1,3);DRTIB1(1,3)];
names = {'vic0','vic1','vic2','vic3'};

plot3(x,y,z,'o', 'Color','r');
text(x,y,z,names,'HorizontalAlignment','right','VerticalAlignment','bottom','Color','r');
hold on 
O = DRTIB0(1,:);
A = DRTIB1(1,:) - O;
L = DRTIB2(1,:) - O;
P = DRTIB3(1,:) - O;
v = quiver3(O(1),O(2),O(3),A(1),A(2),A(3),'Color','r','DisplayName','Vicon');
quiver3(O(1),O(2),O(3),L(1),L(2),L(3),'Color','r');
quiver3(O(1),O(2),O(3),P(1),P(2),P(3),'Color','r');

% -- Create/Plot openOFM dynamic axes (first frame) --------------------
x = [O_dyn(1,1);A_dyn(1,1);L_dyn(1,1);P_dyn(1,1)];
y = [O_dyn(1,2);A_dyn(1,2);L_dyn(1,2);P_dyn(1,2)];
z = [O_dyn(1,3);A_dyn(1,3);L_dyn(1,3);P_dyn(1,3)];
names = {'our0','our1','our2','our3'};
hold on
plot3(x,y,z,'d','Color','b')
text(x,y,z,names,'HorizontalAlignment','left','VerticalAlignment','top','Color','b');
hold on
O = O_dyn(1,:);
A_ofm = A_dyn(1,:) - O;
L_ofm = L_dyn(1,:) - O;
P_ofm = P_dyn(1,:) - O;
o = quiver3(O(1),O(2),O(3),A_ofm(1),A_ofm(2),A_ofm(3),'Color','b','DisplayName','openOFM');
quiver3(O(1),O(2),O(3),L_ofm(1),L_ofm(2),L_ofm(3),'Color','b');
quiver3(O(1),O(2),O(3),P_ofm(1),P_ofm(2),P_ofm(3),'Color','b');
legend([v,o])
title('Dynamic Tibia axes check')
grid on
box on

% compare angles and add to plot?
a = angle(A, A_ofm, 'deg');
p = angle(P, P_ofm, 'deg');
l = angle(L, L_ofm, 'deg');

annotation('textbox', [0.7, 0.3, 0.1, 0.1], 'String', ['3 diff = ', num2str(a) ' deg'])
annotation('textbox', [0.7, 0.4, 0.1, 0.1], 'String', ['2 diff = ', num2str(l) ' deg'])
annotation('textbox', [0.7, 0.5, 0.1, 0.1], 'String', ['1 diff = ', num2str(p) ' deg'])
end