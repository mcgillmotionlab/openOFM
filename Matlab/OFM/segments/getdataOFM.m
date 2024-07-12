function ort = getdataOFM(d)

% xyz order translates directly to 123.
% This is accounted for in groodsuntay.m

x = (d{2}-d{1})/10;   % "Forward" - Origin:          Creates anterior vector
y = (d{3}-d{1})/10;   % "Side" - Origin:            Creates lateral vector (right side), medial vector (left side)
z = (d{4}-d{1})/10;   % "Up" - Origin:            Creates vector along long axis of bone

rw = length(x);
ort = cell(rw,1);
for i = 1:rw
    ort{i} = [x(i,:);y(i,:);z(i,:)];     %for updated grood suntay version
end