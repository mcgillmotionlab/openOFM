function [rep_p1, rep_p2, rep_p3, rep_p4] = replace4(p1,p2,p3,p4)

% [rep_p1, rep_p2, rep_p3, rep_p4] = REPLACE4(p1,p2,p3,p4) calculates a 
% marker’s average position in a local coordinate system defined by the 
% segment’s 3 additional markers and transforms the average position back 
% to global coordinate system
%
% ARGUMENTS
%   p1,p2,p3,p4                    ... n x 3 array, 4 markers in a segments  
%
% RETURNS
%   rep_p1, rep_p2, rep_p3, rep_p4 ... n x 3 array, average position of the
%                                      4 markers in the GCS



% Move p1 to local system 234

p1_vec_lcl = zeros(size(p1));
for i = 1:size(p1,1)
    % Create system 234 for each frame of trial
    [~,~,~,~,s234] = create_lcs(p3(i,:),p2(i,:)-p3(i,:),p3(i,:)-p4(i,:),'xyz');
    % Transform to local for each frame of trial
    p1_vec_lcl(i,:) = ctransform(gunit,s234,p1(i,:)-p3(i,:));    
end

% Calculate average location of p1 in system 234
if size(p1,1) > 1
    p1_vec_lcl_av = mean(p1_vec_lcl);
else
    p1_vec_lcl_av = p1_vec_lcl;
end

% Move the average location of p1 in system 234 back to global
p1_vec_gbl = zeros(size(p1));
new_p1 = zeros(size(p1));
rep_p1 = zeros(size(p1));
for i = 1:size(p1,1)
    % Create system 234 for each frame of trial
    [~,~,~,~,s234] = create_lcs(p3(i,:),p2(i,:)-p3(i,:),p3(i,:)-p4(i,:),'xyz');
    % Transform average location of p1 in system 234 back to global for
    % every frame of trial
    p1_vec_gbl(i,:) = ctransform(s234,gunit,p1_vec_lcl_av);
    % Add position back to local origin to obtain marker position 
    new_p1(i,:) = p1_vec_gbl(i,:) + p3(i,:);
    % Create average of new_p1 and original p1
    rep_p1(i,:) = (new_p1(i,:) + p1(i,:))/2;
end

%-------------------------------------------------------------------------%
%-------------------------------------------------------------------------%

% Create system 341

p2_vec_lcl = zeros(size(p2));
for i = 1:size(p2,1)
    [~,~,~,~,s341] = create_lcs(p4(i,:),p3(i,:)-p4(i,:),p4(i,:)-p1(i,:),'xyz');
    p2_vec_lcl(i,:) = ctransform(gunit,s341,p2(i,:)-p4(i,:));
end

if size(p2,1) > 1
    p2_vec_lcl_av = mean(p2_vec_lcl);
else
    p2_vec_lcl_av = p2_vec_lcl;
end

p2_vec_gbl = zeros(size(p2));
new_p2 = zeros(size(p2));
rep_p2 = zeros(size(p2));
for i = 1:size(p2,1)
    [~,~,~,~,s341] = create_lcs(p4(i,:),p3(i,:)-p4(i,:),p4(i,:)-p1(i,:),'xyz');
    p2_vec_gbl(i,:) = ctransform(s341,gunit,p2_vec_lcl_av);
    new_p2(i,:) = p2_vec_gbl(i,:) + p4(i,:);
    rep_p2(i,:) = (new_p2(i,:) + p2(i,:))/2;
end

%-------------------------------------------------------------------------%
%-------------------------------------------------------------------------%

% Create system 412

p3_vec_lcl = zeros(size(p3));
for i = 1:size(p3,1)
    [~,~,~,~,s412] = create_lcs(p1(i,:),p4(i,:)-p1(i,:),p1(i,:)-p2(i,:),'xyz');
    p3_vec_lcl(i,:) = ctransform(gunit,s412,p3(i,:)-p1(i,:));
end

if size(p3,1) > 1
    p3_vec_lcl_av = mean(p3_vec_lcl);
else
    p3_vec_lcl_av = p3_vec_lcl;
end

p3_vec_gbl = zeros(size(p3));
new_p3 = zeros(size(p3));
rep_p3 = zeros(size(p3));
for i = 1:size(p3,1)
    [~,~,~,~,s412] = create_lcs(p1(i,:),p4(i,:)-p1(i,:),p1(i,:)-p2(i,:),'xyz');
    p3_vec_gbl(i,:) = ctransform(s412,gunit,p3_vec_lcl_av);
    new_p3(i,:) = p3_vec_gbl(i,:) + p1(i,:);
    rep_p3(i,:) = (new_p3(i,:) + p3(i,:))/2;
end

%-------------------------------------------------------------------------%
%-------------------------------------------------------------------------%

% Create system 123

p4_vec_lcl = zeros(size(p4));
for i = 1:size(p4,1)
    [~,~,~,~,s123] = create_lcs(p2(i,:),p1(i,:)-p2(i,:),p2(i,:)-p3(i,:),'xyz');
    p4_vec_lcl(i,:) = ctransform(gunit,s123,p4(i,:)-p2(i,:));
end

if size(p1,1) > 1
    p4_vec_lcl_av = mean(p4_vec_lcl);
else
    p4_vec_lcl_av = p4_vec_lcl;
end

p4_vec_gbl = zeros(size(p4));
new_p4 = zeros(size(p4));
rep_p4 = zeros(size(p4));
for i = 1:size(p4,1)
    [~,~,~,~,s123] = create_lcs(p2(i,:),p1(i,:)-p2(i,:),p2(i,:)-p3(i,:),'xyz');
    p4_vec_gbl(i,:) = ctransform(s123,gunit,p4_vec_lcl_av);
    new_p4(i,:) = p4_vec_gbl(i,:) + p2(i,:);
    rep_p4(i,:) = (new_p4(i,:) + p4(i,:))/2;
end
end











