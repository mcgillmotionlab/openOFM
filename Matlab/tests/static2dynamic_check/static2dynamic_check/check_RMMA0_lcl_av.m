function NRMSE_RMMA0 = check_RMMA0_lcl_av (RMMA0_lcl_av, data)

% NRMSE_RMMA0 = CHECK_RMMA0_LCL_AV(RD1M0_lcl_av, data) calculates the
% NRMSE difference between openOFM's RMMA0_lcl_av and vicon's RMMA0_lcl_av
%
% ARGUMENTS
% data          ....   struct containing marker data
% RMMA0_lcl_av  ....   average of the tibia virtual marker RMMA0 in LCS 
%                      of static trial
%
% RETURNS
% NRMSE_RMMA0   ....   NRMSE between openOFM and vicon RMMA0_lcl_av


RMMA0_lcl_av_vicon = [data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRMMAX.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRMMAY.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRMMAZ.data];
            
%test_RMMA0_lcl_av = RMMA0_lcl_av_vicon - RMMA0_lcl_av;

NRMSE_RMMA0 = nrmse(RMMA0_lcl_av_vicon, RMMA0_lcl_av);
end