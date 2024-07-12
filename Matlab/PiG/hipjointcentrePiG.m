function data = hipjointcentrePiG(data)

% data = HIPJOINTCENTREPIG(data) computes left and right hip joint centers for
% plug-in gait (PiG) marker data
%
% ARGUMENTS
%  data      ... struct containing PiG markers. Required markers are 'RASI','LASI','SACR'
%                or 'RASI','LASI','RPSI','LPSI'
%
% RETURNS
%  data      ... struct data with appended hip joint center virtual marker as RHipJC and LHipJC.
%
% NOTES
% - computation method based on Davis et al. "A gait analysis data collection and reduction
%   technique". Hum Mov Sci. 1991. (see also PiG manual)

% set values from Davis et al. 1991
COSBETA  = cos(0.314);                                              % 18.0 deg Davis 1991
SINBETA  = sin(0.314);
COSTHETA = cos(0.496);                                              % 28.4 deg Davis 1991
SINTHETA = sin(0.496);

% Extract pelvis marker positions
RASI = data.RASI;
LASI = data.LASI;

if isfield(data,'RPSI')
    RPSI = data.RPSI;
    LPSI = data.LPSI;
    SACR = (RPSI+LPSI)/2;
else
    SACR = data.SACR;
end

% Extract info from data
mDiam = data.MetaInformation.Anthro.MarkerDiameter;
rLegLength = data.MetaInformation.Anthro.RLegLength;
lLegLength = data.MetaInformation.Anthro.LLegLength;
interAsis = data.MetaInformation.Anthro.InterAsisDistance;

% compute basic quantities
legLength = mean([rLegLength lLegLength]);
asisTroc = (0.1288*legLength)-48.56;                       % PiG manual

% Define pelvis coordinate system
PELO = (LASI + RASI)/2;                                                % origin (O)
PELy = makeunit(LASI-PELO);                                            % lateral (L)
PELtemp = SACR - PELO;                                                 % temp anterior
PELz = makeunit(cross(PELy,PELtemp));                                  % proximal (P)
PELx = makeunit(cross(PELy,PELz));                                     % anterior (A)

   
% Compute hip joint centers in global coordinates
side = {'R','L'};
for i = 1:length(side)
    
    % Compute hip joint center in pelvis coordinate system (PCS)
    C = (legLength*0.115) - 15.3;                                      % (4) Davis 1991
    HipPCSx = C*COSTHETA*SINBETA - (asisTroc + mDiam/2)*COSBETA;       % (5) Davis 1991 (A)
    HipPCSy = -(C*SINTHETA - (interAsis/2));                           % (6) Davis 1991 (L)
    HipPCSz = -C*COSTHETA*COSBETA - (asisTroc + mDiam/2)*SINBETA;      % (7) Davis 1991 (P)
   
    if side{i}=='R'
        HipPCSy =  -HipPCSy;
    end
    
    HipPCS = [HipPCSx HipPCSy HipPCSz];
    
    % Transform from pelvis coordinate system to global coordinate system
    HipGCS = ones(size(RASI));
    GCS = gunit;
    rows= size(RASI,1);
    for j = 1:rows
        PCS = [PELx(j,:); PELy(j,:) ; PELz(j,:)];
        HipGCS(j,:) = ctransform(PCS,GCS,HipPCS)+PELO(j,:);
    end
    
    % add data to struct
    data.([side{i},'HipJC']) = HipGCS;
    
end



