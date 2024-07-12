function NRMSE_RHFplantar = check_RHFplantar_lcl_av (RHFPlantar_lcl_av, data)

% NRMSE_RHFplantar = CHECK_RHFPLANTAR_LCL_AV(RD1M0_lcl_av, data) calculates the
% NRMSE difference between openOFM's RHFplantar_lcl_av and vicon's RHFplantar_lcl_av
%
% ARGUMENTS
% data               ....   struct containing marker data
% RHFplantar_lcl_av  ....   average of the hindfoot virtual marker RHFplantar in LCS 
%                           of static trial
%
% RETURNS
% NRMSE_RHFplantar   ....   NRMSE between openOFM and vicon RHFplantar_lcl_av

RHFplantar_lcl_av_vicon = [data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRHFplantarX.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRHFplantarY.data, ...
                data.zoosystem.OtherMetaInfo.Parameter.PROCESSING.percentRHFplantarZ.data];
 

 NRMSE_RHFplantar = nrmse(RHFplantar_lcl_av_vicon, RHFPlantar_lcl_av);
end