function [floatax,floatax_isb, prox_x,dist_x,prox_y,dist_y,prox_z,dist_z] = makeax(pax,dax)

prox_x = zeros(length(pax),3);
prox_y = zeros(length(pax),3);
prox_z = zeros(length(pax),3);

dist_x = zeros(length(pax),3);
dist_y = zeros(length(pax),3);
dist_z = zeros(length(pax),3);

floatax = zeros(length(pax),3);
floatax_isb = zeros(length(pax),3);

for i = 1:length(pax)
    prox_x(i,:) = makeunit(pax{i}(1,:));
    prox_y(i,:) = makeunit(pax{i}(2,:));
    prox_z(i,:) = makeunit(pax{i}(3,:));
    
    dist_x(i,:) = makeunit(dax{i}(1,:));
    dist_y(i,:) = makeunit(dax{i}(2,:));
    dist_z(i,:) = makeunit(dax{i}(3,:));
    
    floatax(i,:) = cross(prox_z(i,:),dist_x(i,:));
    floatax_isb(i, :) = cross(dist_y(i, :), prox_z(i, :));
end

floatax = makeunit(floatax);
floatax_isb = makeunit(floatax_isb);
prox_x = makeunit(prox_x);
dist_x = makeunit(dist_x);
prox_y = makeunit(prox_y);
dist_y = makeunit(dist_y);
prox_z = makeunit(prox_z);
dist_z = makeunit(dist_z);