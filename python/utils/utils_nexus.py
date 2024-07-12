import os
import numpy as np
from viconnexusapi import ViconNexus


def get_nexus_data(settings):
    vicon = ViconNexus.ViconNexus()

    region = vicon.GetTrialRegionOfInterest()

    subject = vicon.GetSubjectNames()[0]
    _, template, active = vicon.GetSubjectInfo()

    markers = vicon.GetMarkerNames(subject)
    modeled_markers = vicon.GetModelOutputNames(subject)

    data = {'parameters': {}}
    data['parameters']['PROCESSING'] = {}

    for marker in markers:
        data[marker] = {}
        (X1, Y1, Z1, _) = vicon.GetTrajectory(subject, marker)
        data[marker] = np.array([X1, Y1, Z1]).T[region[0] - 1:region[1]]

    if 'RHE1' in modeled_markers:
        modeled_markers = ['RHE1', 'LHE1']
        for marker in modeled_markers:
            data[marker] = {}
            (coords, _) = vicon.GetModelOutput(subject, marker)
            data[marker] = np.array(coords).T[region[0] - 1:region[1]]

    settings['processing'] = dict(LHindFootFlat=vicon.GetSubjectParam(subject, 'LeftHindFootFlat')[0],
                                  RHindFootFlat=vicon.GetSubjectParam(subject, 'RightHindFootFlat')[0],
                                  LUseFloorFF=vicon.GetSubjectParam(subject, 'LeftUseFloorFF')[0],
                                  RUseFloorFF=vicon.GetSubjectParam(subject, 'RightUseFloorFF')[0],
                                  )

    if settings['trial_type'] == 'dynamic':

        params = vicon.GetSubjectParamNames(subject)
        for param in params:
            param_short = param.replace('Right', 'R')
            param_short = param_short.replace('Left', 'L')
            data['parameters']['PROCESSING'][param_short] = {}
            data['parameters']['PROCESSING'][param_short]['value'], active = vicon.GetSubjectParam(subject, param)

    return data, settings


def set_nexus_data(data, trial_type):
    from viconnexusapi import ViconNexus
    vicon = ViconNexus.ViconNexus()

    # path, folder = vicon.GetTrialName()
    #
    frames = vicon.GetFrameCount()
    region = vicon.GetTrialRegionOfInterest()
    size = region[1] - region[0] + 1

    subject = vicon.GetSubjectNames()[0]
    _, template, active = vicon.GetSubjectInfo()

    if trial_type == 'static':
        # create new dictionary with only openOFM processing parameters
        params = dict(filter(lambda item: 'openOFM' in item[0], data['parameters']['PROCESSING'].items()))
        outputs = vicon.GetSubjectParamNames(subject)
        for key, value in params.items():
            if key not in outputs:
                vicon.CreateSubjectParam(subject, key, value, 'mm', 0, True)
            else:
                vicon.SetSubjectParam(subject, key, value, True)

    if trial_type == 'dynamic':
        angles = ['RightTIBA', 'RightHFTBA', 'RightFFTBA', 'RightFFHFA', 'RightHXFFA',
                  'LeftTIBA', 'LeftHFTBA', 'LeftFFTBA', 'LeftFFHFA', 'LeftHXFFA',
                  ]
        components = ['X', 'Y', 'Z']
        types = ['Angle', 'Angle', 'Angle']

        # (data, exists) = vicon.GetModelOutput(subject, angles)

        for angle in angles:
            # i = region[0]
            _, exists = vicon.GetModelOutput(subject, angle)
            if angle == 'RightHXFFA' or angle == 'LeftHXFFA':
                component = np.zeros((3, frames))
                component[0, region[0] - 1:region[1]] = data[angle + '_x']
                component[1, region[0] - 1:region[1]] = data[angle + '_y']
            else:
                component = np.zeros((3, frames))
                component[0, region[0] - 1:region[1]] = data[angle + '_x']
                component[1, region[0] - 1:region[1]] = data[angle + '_y']
                component[2, region[0] - 1:region[1]] = data[angle + '_z']
            outputs = vicon.GetModelOutputNames(subject)
            if angle not in outputs:
                vicon.CreateModelOutput(subject, angle, 'Angles', components, types)
                exists = [False] * frames
                exists[region[0] - 1:region[1]] = [True for i in range(size)]
            vicon.SetModelOutput(subject, angle, component, exists)
