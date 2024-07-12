function mrk_dyn = static2dynamic(O_dyn, A_dyn, L_dyn, P_dyn, mrk_lcl_av)

% mrk_dyn = STATIC2DYNAMIC(O_dyn, A_dyn, L_dyn, P_dyn, mrk_lcl_av)
% creates virtual static marker in dynamic trial
%
% ARGUMENTS
%   O_dyn       ... n x 3 array: origin of the LCS of dynamic trial
%   A_dyn       ... n x 3 array: anterior axis of the LCS of dynamic trial
%   L_dyn       ... n x 3 array: lateral axis of the LCS of dynamic trial
%   P_dyn       ... n x 3 array: proximal axis of the LCS of dynamic trial
%   mrk_lcl_av  ... n x 3 array: virtual markers in LCS of static trial
%
% RETURNS
%   mrk_dyn     ... n x 3 array: dynamic version of the static marker

mrk_dyn = zeros(size(O_dyn));
for i = 1:length(mrk_dyn)
    
    % create LCS for dynamic trial at each frame
    a_prime = makeunit(A_dyn(i, :) - O_dyn(i, :));
    l_prime = makeunit(L_dyn(i, :) - O_dyn(i, :));
    p_prime = makeunit(P_dyn(i, :) - O_dyn(i, :));
    lcs_prime = [a_prime; l_prime; p_prime];
    
    % transform marker from lcs_prime to gcs
    mrk_lcl_prime = ctransform(lcs_prime, gunit, mrk_lcl_av);
    
    % translate marker position from 0 to origin of LCS dynamic
    mrk_dyn(i, :) = mrk_lcl_prime + O_dyn(i,:);
end