from OFM.virtual_markers import create_virtual_markers
from utils.utils import is_nexus, get_python_settings
from utils.utils import get_data, set_data

TRIAL_TYPE = 'static'


def openOFM_static(settings):

    # 1: Access static calibration file
    if settings['nexus']:
        sdata, settings = get_nexus_data(settings)
    else:
        sdata, _ = get_data(settings)

    # 2: Create dynamic version of virtual markers present in static trial + compute phi and omega
    sdata = create_virtual_markers(sdata, settings)

    if settings['nexus']:
        set_nexus_data(sdata, TRIAL_TYPE)
    else:
        set_data(sdata, settings)

    return sdata


if __name__ == "__main__":

    # initialize settings
    settings_params = dict(trial_type=TRIAL_TYPE)

    # check if user is using python or nexus and load appropriate settings
    nexus = is_nexus()

    if nexus:
        import sys
        from utils.utils_nexus import set_nexus_data, get_nexus_data
        settings_params['nexus'] = nexus
        settings_params['version'] = sys.argv[1]
    else:
        import argparse
        parser = argparse.ArgumentParser(
            description='openOFM static trial processing',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        # set arguments
        parser.add_argument('--version', default='1.0', choices={'1.0', '1.1'}, help='Version of openOFM to run')
        parser.add_argument('--data_dir', default='Data_Sample/Sample', help='Name of subfolder relative to root')
        parser.add_argument('--file_name', default='static.c3d', help='name of static trial file to process')
        parser.add_argument('--use_settings', action="store_true",
                            help='If true, looks for settings.yml in the subject folder. '
                                 'If false, looks for settings in .c3d file')
        args = vars(parser.parse_args())
        settings_params.update(args)
        settings_params['nexus'] = nexus
        if settings_params['use_settings']:
            settings_params.update(get_python_settings(args))

    # run openOFM static
    openOFM_static(settings=settings_params)
