from PiG.pig import hipjointcentrePiG_data, kneejointcenterPiG, anklejointcenterPiG
from OFM.virtual_markers import animate_virtual_markers
from OFM.segments import segments
from OFM.kinematics import kinematics
from utils.utils import get_data, get_python_settings, is_nexus, make_plot_title
from plotting.plotting import plot_angles

TRIAL_TYPE = 'dynamic'


def openOFM_dynamic(settings):
    # 1: Access static calibration file
    if settings['nexus']:
        data, settings = get_nexus_data(settings)
    else:
        data, settings = get_data(settings)

    if settings['version'] == '1.0':
        # % compute hip, knee and ankle joint center
        data = hipjointcentrePiG_data(data)
        data = kneejointcenterPiG(data)
        data = anklejointcenterPiG(data)

    # 2: Create dynamic version of virtual markers present in static trial + compute phi and omega
    data = animate_virtual_markers(data, settings)

    # 3: Create virtual segment embedded axes
    data, r, jnt = segments(data, settings['version'])

    # 4: Compute joint angles according to Grood and Suntay method
    data = kinematics(data, r, jnt, settings['version'])

    if settings['nexus']:
        set_nexus_data(data, TRIAL_TYPE)

    # 5: Plot results
    if settings['make_plot']:
        plot_title = make_plot_title(settings)
        plot_angles(data=data, plot_title=plot_title)

    return data


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
            description='openOFM dynamic trial processing',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        # set arguments
        parser.add_argument('--version', default='1.0', choices={'1.0', '1.1'}, help='Version of openOFM to run')
        parser.add_argument('--data_dir', default='Data_Sample/Sample', help='Name of subfolder relative to root')
        parser.add_argument('--file_name', default='dynamic.c3d', help='name of dynamic trial to process')
        parser.add_argument('--use_settings', action="store_true",
                            help='If true, looks for settings.yml in the subject folder. '
                                 'If false, looks for settings in .c3d file')
        parser.add_argument('--make_plot', action="store_true",
                            help='If true, makes a plot showing kinematic results. '
                                 'If false, no plot is made')
        args = vars(parser.parse_args())
        settings_params.update(args)
        settings_params['nexus'] = nexus
        if settings_params['use_settings']:
            settings_params.update(get_python_settings(args))

    # run openOFM dynamic
    openOFM_dynamic(settings=settings_params)
