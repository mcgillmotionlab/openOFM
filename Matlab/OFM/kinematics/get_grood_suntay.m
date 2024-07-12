function KIN = get_grood_suntay(r,jnt,dir,version)

% Depending on the version, computes angles using different Grood and
% Suntay methods


for i = 1:length(jnt(:,1))
    if version == "1.0"
        [KIN.(jnt{i,1}).alpha, KIN.(jnt{i,1}).beta, KIN.(jnt{i,1}).gamma] = groodsuntay_1_0(r,jnt(i, :),dir);
    elseif version =="1.1"
        [KIN.(jnt{i,1}).alpha, KIN.(jnt{i,1}).beta, KIN.(jnt{i,1}).gamma] = groodsuntay(r,jnt(i, :),dir);
    end
end