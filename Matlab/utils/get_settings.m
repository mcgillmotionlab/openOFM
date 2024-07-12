function settings = get_settings(data)


% extract relevant Vicon settings from subjet folder name
settings.LHindFootFlat = data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.LHindFootFlat.data;
settings.RHindFootFlat = data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.RHindFootFlat.data;
settings.RUseFloorFF = data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.RUseFloorFF.data;
settings.LUseFloorFF = data.MetaInformation.OtherMetaInfo.Parameter.PROCESSING.LUseFloorFF.data;

end
