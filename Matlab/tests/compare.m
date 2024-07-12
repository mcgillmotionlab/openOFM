function [difference] = compare(data,v_data)

difference.FOF0 = zeros(3,1);
difference.FOF1 = zeros(3,1);
difference.FOF2 = zeros(3,1);
difference.FOF3 = zeros(3,1);
difference.TIB0 = zeros(3,1);
difference.TIB1 = zeros(3,1);
difference.TIB2 = zeros(3,1);
difference.TIB3 = zeros(3,1);


sides = {'R','L'};        
for j = 1:length(sides)
    side = sides{j};
    subch = {'PlaDor','InvEve','IntExt'}; % TibiaLab
    for k = 1:length(subch)
        difference.TIB0(k) = nrmse(v_data.([side,'TIB0']).line(:,k),data.([side,'TIB0']).line(:,k));
        difference.TIB1(k) = nrmse(v_data.([side,'TIB1']).line(:,k),data.([side,'TIB1']).line(:,k));
        difference.TIB2(k) = nrmse(v_data.([side,'TIB2']).line(:,k),data.([side,'TIB2']).line(:,k));
        difference.TIB3(k) = nrmse(v_data.([side,'TIB3']).line(:,k),data.([side,'TIB3']).line(:,k));
    end
    subch = {'PlaDor','InvEve','IntExt'}; % Hindfoot
    for k = 1:length(subch)
        difference.HDF0(k) = nrmse(v_data.([side,'HDF0']).line(:,k),data.([side,'HDF0']).line(:,k));
        difference.HDF1(k) = nrmse(v_data.([side,'HDF1']).line(:,k),data.([side,'HDF1']).line(:,k));
        difference.HDF2(k) = nrmse(v_data.([side,'HDF2']).line(:,k),data.([side,'HDF2']).line(:,k));
       difference. HDF3(k) = nrmse(v_data.([side,'HDF3']).line(:,k),data.([side,'HDF3']).line(:,k));
    end
        subch = {'PlaDor','InvEve','IntExt'}; % Forefoot
    for k = 1:length(subch)
        difference.FOF0(k) = nrmse(v_data.([side,'FOF0']).line(:,k),data.([side,'FOF0']).line(:,k));
        difference.FOF1(k) = nrmse(v_data.([side,'FOF1']).line(:,k),data.([side,'FOF1']).line(:,k));
        difference.FOF2(k) = nrmse(v_data.([side,'FOF2']).line(:,k),data.([side,'FOF2']).line(:,k));
       difference. FOF3(k) = nrmse(v_data.([side,'FOF3']).line(:,k),data.([side,'FOF3']).line(:,k));
    end
end

end