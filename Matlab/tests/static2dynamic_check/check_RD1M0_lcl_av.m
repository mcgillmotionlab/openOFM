function NRMSE_RD1M0 = check_RD1M0_lcl_av (RD1M0_lcl_av, data)

% NRMSE_RD1M0 = CHECK_RD1M0_LCL_AV(RD1M0_lcl_av, data) calculates the
% NRMSE difference between openOFM's RD1M0_lcl_av and vicon's RD1M0_lcl_av
%
% ARGUMENTS
% data          ....   struct containing marker data
% RD1M0_lcl_av  ....   average of the forefoot virtual marker RD1M0 in LCS 
%                      of static trial
%
% RETURNS
% NRMSE_RD1M0   ....   NRMSE between openOFM and vicon RD1M0_lcl_av


RD1M0_lcl_av_vicon = [data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRD1M0X.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRD1M0Y.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRD1M0Z.data];


NRMSE_RD1M0 = nrmse(RD1M0_lcl_av_vicon, RD1M0_lcl_av);

end