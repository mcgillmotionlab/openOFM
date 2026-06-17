import os
from typing import Any

from openofm.utils.utils import find_repo_root, c3d_to_dict, get_params, make_plot_title, get_nrmse
from openofm.plotting.plotting import plot_angles
from openofm.ofm import OFM

# global settings
static_trial = 'static.c3d'
dynamic_trial = 'dynamic.c3d'
static_trial_processed = 'static_processed.c3d'
dynamic_trial_processed = 'dynamic_processed.c3d'



def ofm_validate():
    """script to demonstrate validation of open OFM against Vicon processed data"""

    settings: dict[str, Any] = {
        "use_settings": False,          # don't look for settings in .c3d file
        "version": '1.0',               # set version of ofm model (use only 1.0 to replicate against Vicon)
        "nexus": False,                 # nexus is always set to False in order to validate the python code
    }

    # get path to validation c3d files
    root_dir = find_repo_root(os.path.dirname(__file__))
    data_dir = os.path.join(root_dir, "Data_Validate")

    for subject in os.listdir(data_dir):
        settings['data_dir'] = os.path.join(data_dir, subject)  # relative to root
        print('validating openOFM using raw and processed data in folder {}'.format(settings['data_dir']))

        # load c3d files processed in Vicon (needed for validation)
        fl_static_processed = os.path.join(root_dir, settings['data_dir'], static_trial_processed)
        fl_dynamic_processed = os.path.join(root_dir, settings['data_dir'], dynamic_trial_processed)
        sdata_processed = c3d_to_dict(fl_static_processed)
        data_processed = c3d_to_dict(fl_dynamic_processed)


        # get settings from the processed file to validate ofm pipeline
        parameter_settings, processing_settings = get_params(sdata_processed)

        # initialize OFM object
        openOFM = OFM(version='1.0')

        # process the static trial
        openOFM.process_static_trial()

        # process the dynamic trial
        openOFM.process_dynamic_trial()

        # compute normalized root mean squared error between vicon generated OFM and openOFM
        #todo: refactor this to allow for computation of nrmse
        # data = get_nrmse(data, data_processed)

        # compare angles between vicon generated OFM and openOFM
        #plot_title = make_plot_title(settings)
        # plot_angles(data=data, vicon_data=data_processed, plot_title=plot_title)






def main() -> None:
    ofm_validate()


if __name__ == "__main__":
    main()