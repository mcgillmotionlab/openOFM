import os
from .dynamic import openOFM_dynamic
from .static import openOFM_static
from .utils.utils import find_repo_root, c3d_to_dict, make_plot_title, get_nrmse
from .plotting.plotting import plot_angles

# global settings
validation_dir = 'Data_Validate'
static_trial = 'static.c3d'
dynamic_trial = 'dynamic.c3d'
static_trial_processed = 'static_processed.c3d'
dynamic_trial_processed = 'dynamic_processed.c3d'


from openofm import openOFM
from utils.utils import fetch_dataset


# initialize openOFM object with version 1.0
ofm = openOFM(version='1.0')


# fetch validation data (downloads from github if not on local machine)
data_dir = fetch_dataset(name='Data_Validate')

# Run validation code
settings = dict(nexus=False)        # nexus is always set to False in order to validate the python code
settings['use_settings'] = False    # looks for settings in .c3d file

ofm.validate(data_dir)
ofm.plot_angles()




def get_validation_settings(sdata_processed: dict, settings: dict) -> dict:
    """Populate settings with parameter values from the Vicon OFM pipeline.

    Parameters
    ----------
    sdata_processed : dict
        Static trial data pre-processed by Vicon, containing a
        ``parameters['PROCESSING']`` block with subject measurements.
    settings : dict
        Existing settings dictionary to extend.

    Returns
    -------
    dict
        Extended settings dictionary with ``'parameters'`` and
        ``'processing'`` sub-dicts populated.
    """
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


# def main() -> None:
#     """Entry point for the ``openofm-validate`` command."""
#     ofm_validate()

#
# if __name__ == "__main__":
