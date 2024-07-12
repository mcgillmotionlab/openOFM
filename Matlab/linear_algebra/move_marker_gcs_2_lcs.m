function m_lcs_static = move_marker_gcs_2_lcs(O, A, L, P, M)
%
% m_lcs_static = MOVE_MARKER_GCS_2_LCS(O, A, L, P, M) moves marker from GCS
% to lcs_static for each available frame
%
% ARGUMENTS
%   O            ... n x 3 array
%                    Origin of the technical axes
%   A            ... n x 3 array
%                    Anterior axis of the segment
%   L            ... n x 3 array
%                    Lateral axis of the segment (medial for right side)
%   P            ... n x 3 array
%                    Proximal axis of the segment
%   M            ... n x 3 array
%                    Medial? axis of the segment
%
% RETURNS
%   m_lcs_static ... n x 3 array
%                    Marker moved from GCS to LCS
%
% NOTES
% 


% move marker from GCS to lcs_static for each available frame
m_lcs_static = zeros(size(O));
for i = 1:length(m_lcs_static(:,1))
    
    % create LCS for static trial at each frame
    a = makeunit(A(i, :) - O(i, :));
    l = makeunit(L(i, :) - O(i, :));
    p = makeunit(P(i, :) - O(i, :));
    lcs_static = [a; l; p];
    
    % translate marker to origin of GCS
    m_static= M(i,:)- O(i,:);
    
    % transform marker position from GCS to lcs_static
    m_lcs_static(i, :) = ctransform(gunit, lcs_static, m_static);
end