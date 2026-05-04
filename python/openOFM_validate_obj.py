import os
from openOFM_dynamic import openOFM_dynamic
from openOFM_static import openOFM_static
from utils.utils import find_repo_root, c3d_to_dict, make_plot_title, get_nrmse
from plotting.plotting import plot_angles

# global settings
validation_dir = 'Data_Validate'
static_trial = 'static.c3d'
dynamic_trial = 'dynamic.c3d'
static_trial_processed = 'static_processed.c3d'
dynamic_trial_processed = 'dynamic_processed.c3d'


def ofm_validate():
    """script to demonstrate validation of open OFM against Vicon processed data"""

    # general settings for all validation trials
    settings = dict(nexus=False)        # nexus is always set to False in order to validate the python code
    settings['version'] = '1.0'        # set version of ofm model (use only 1.0 to replicate against Vicon)
    settings['use_settings'] = False   # looks for settings in .c3d file

    # get path to validation c3d files
    ROOT_DIR = find_repo_root(os.path.dirname(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, validation_dir)

    for subject in os.listdir(DATA_DIR):
        settings['data_dir'] = os.path.join(validation_dir, subject)  # relative to root
        print('validating openOFM using raw and processed data in folder {}'.format(settings['data_dir']))

        # get path to validation files
        fl_static_processed = os.path.join(ROOT_DIR, settings['data_dir'], static_trial_processed)
        fl_dynamic_processed = os.path.join(ROOT_DIR, settings['data_dir'], dynamic_trial_processed)

        # load c3d files to dictionary
        sdata_processed = c3d_to_dict(fl_static_processed)
        data_processed = c3d_to_dict(fl_dynamic_processed)

        # update settings to include parameters computed by OFM pipeline
        settings.update(get_validation_settings(sdata_processed, settings))

        # run openOFM static
        settings['trial_type'] = 'static'
        settings['file_name'] = static_trial
        _ = openOFM_static(settings=settings)

        # run openOFM dynamic
        settings['trial_type'] = 'dynamic'
        settings['file_name'] = dynamic_trial
        settings['make_plot'] = False
        data = openOFM_dynamic(settings=settings)

        # compute normalized root mean squared error between vicon generated OFM and openOFM
        data = get_nrmse(data, data_processed)

        # compare angles between vicon generated OFM and openOFM
        plot_title = make_plot_title(settings)
        plot_angles(data=data, vicon_data=data_processed, plot_title=plot_title)


def get_validation_settings(sdata_processed, settings):
    """ populates settings parameters with values computed by Vicon OFM pipleline for validation"""
    params = sdata_processed['parameters']['PROCESSING']
    settings['parameters'] = {}
    settings['parameters']['MarkerDiameter'] = int(params['MarkerDiameter']['value'][0])
    settings['parameters']['InterAsisDistance'] = int(params['InterAsisDistance']['value'][0])
    settings['parameters']['RLegLength'] = int(params['RLegLength']['value'][0])
    settings['parameters']['LLegLength'] = int(params['LLegLength']['value'][0])
    settings['parameters']['RKneeWidth'] = int(params['RKneeWidth']['value'][0])
    settings['parameters']['LKneeWidth'] = int(params['LKneeWidth']['value'][0])
    settings['parameters']['RAnkleWidth'] = int(params['RAnkleWidth']['value'][0])
    settings['parameters']['LAnkleWidth'] = int(params['LAnkleWidth']['value'][0])
    settings['parameters']['RThighRotation'] = int(params['RThighRotation']['value'][0])
    settings['parameters']['LThighRotation'] = int(params['LThighRotation']['value'][0])
    settings['parameters']['RShankRotation'] = int(params['RShankRotation']['value'][0])
    settings['parameters']['LShankRotation'] = int(params['LShankRotation']['value'][0])

    settings['processing'] = {}
    settings['processing']['RHindFootFlat'] = int(params['RHindFootFlat']['value'][0].astype(int))
    settings['processing']['LHindFootFlat'] = int(params['LHindFootFlat']['value'][0].astype(int))
    settings['processing']['RUseFloorFF'] = int(params['RUseFloorFF']['value'][0].astype(int))
    settings['processing']['LUseFloorFF'] = int(params['LUseFloorFF']['value'][0].astype(int))

    return settings


if __name__ == "__main__":
    ofm_validate()
