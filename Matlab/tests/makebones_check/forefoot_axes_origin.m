function forefoot_axes_origin(axis1,axis2,axis3,RprojTOE,data)

% compare forefoot angles calculated from Vicon and openOFM

% --- Extract markers ------------------------------
vicon_RFOF0 = data.RFOF0.line;
vicon_RFOF1 = data.RFOF1.line;
vicon_RFOF2 = data.RFOF2.line;
vicon_RFOF3 = data.RFOF3.line;


RFOF0 = RprojTOE;
RFOF1 = RFOF0 + 50*axis1;
RFOF2 = RFOF0 + 50*axis2;
RFOF3 = RFOF0 + 50*axis3;

zeroOrigin = zeros(size(RFOF0));

% -- Create/Plot vicon forefoot axes (first frame) --------------------
figure
x = [vicon_RFOF0(1,1);vicon_RFOF1(1,1);vicon_RFOF2(1,1);vicon_RFOF3(1,1)];
y = [vicon_RFOF0(1,2);vicon_RFOF1(1,2);vicon_RFOF2(1,2);vicon_RFOF3(1,2)];
z = [vicon_RFOF0(1,3);vicon_RFOF1(1,3);vicon_RFOF2(1,3);vicon_RFOF3(1,3)];
names = {'vicon0','vicon1','vicon2','vicon3'};

plot3(x,y,z,'o', 'Color','r');
text(x,y,z,names,'HorizontalAlignment','right','VerticalAlignment','bottom','Color','r');
hold on 
O = zeroOrigin(1,:);
A = vicon_RFOF3(1,:) - O;
L = vicon_RFOF2(1,:) - O;
P = vicon_RFOF1(1,:) - O;
v = quiver3(O(1),O(2),O(3),A(1),A(2),A(3),'Color','r','DisplayName','Vicon');
%quiver3(O(1),O(2),O(3),L(1),L(2),L(3),'Color','r');
%quiver3(O(1),O(2),O(3),P(1),P(2),P(3),'Color','r');

% -- Create/Plot openOFM forefoot axes (first frame) --------------------
x = [RFOF0(1,1);RFOF1(1,1);RFOF2(1,1);RFOF3(1,1)];
y = [RFOF0(1,2);RFOF1(1,2);RFOF2(1,2);RFOF3(1,2)];
z = [RFOF0(1,3);RFOF1(1,3);RFOF2(1,3);RFOF3(1,3)];
names = {'O','P','L','A'};
hold on
plot3(x,y,z,'d','Color','b')
text(x,y,z,names,'HorizontalAlignment','left','VerticalAlignment','top','Color','b');
hold on
O = zeroOrigin(1,:);
A_ofm = RFOF3(1,:) - O;
L_ofm = RFOF2(1,:) - O;
P_ofm = RFOF1(1,:) - O;
o = quiver3(O(1),O(2),O(3),A_ofm(1),A_ofm(2),A_ofm(3),'Color','b','DisplayName','openOFM');
quiver3(O(1),O(2),O(3),L_ofm(1),L_ofm(2),L_ofm(3),'Color','b');
quiver3(O(1),O(2),O(3),P_ofm(1),P_ofm(2),P_ofm(3),'Color','b');
legend([v,o])
title ('Forefoot origin check')
grid on
box on

% compare angles and add to plot?
a = angle(A, A_ofm, 'deg');
p = angle(P, P_ofm, 'deg');
l = angle(L, L_ofm, 'deg');

annotation('textbox', [0.7, 0.3, 0.1, 0.1], 'String', ['3 diff = ', num2str(a) ' deg'])
annotation('textbox', [0.7, 0.4, 0.1, 0.1], 'String', ['2 diff = ', num2str(l) ' deg'])
annotation('textbox', [0.7, 0.5, 0.1, 0.1], 'String', ['1 diff = ', num2str(p) ' deg'])