function NRMSE_RPCA0 = check_RPCA0_lcl_av (RPCA0_lcl_av, data)

% NRMSE_RD1M0 = CHECK_RPCA0_LCL_AV(RPCA0_lcl_av, data) calculates the
% NRMSE difference between openOFM's RPCA0_lcl_av and vicon's RPCA0_lcl_av
%
% ARGUMENTS
% data          ....   struct containing marker data
% RPCA0_lcl_av  ....   average of the hindfoot virtual marker RPCA0 in LCS 
%                      of static trial
%
% RETURNS
% NRMSE_RPCA0   ....   NRMSE between openOFM and vicon RPCA0_lcl_av

RPCA_lcl_av_vicon = [data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRPCAX.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRPCAY.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRPCAZ.data];
            
%test_RPCA0_lcl_av = RPCA_lcl_av_vicon - RPCA0_lcl_av
NRMSE_RPCA0 = nrmse(RPCA_lcl_av_vicon, RPCA0_lcl_av);
end