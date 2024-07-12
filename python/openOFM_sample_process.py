import yaml
import os

from OFM.virtual_markers import create_virtual_markers
from utils.utils import c3d_to_dict, find_vcs_root, get_python_settings,  make_plot_title
from PiG.pig import hipjointcentrePiG_data, kneejointcenterPiG, anklejointcenterPiG
from OFM.virtual_markers import animate_virtual_markers
from OFM.segments import segments
from OFM.kinematics import kinematics
from plotting.plotting import plot_angles


# path to raw static file, raw dynamic file, and settings file
DATA_DIR = os.path.join(find_vcs_root(os.path.dirname(__file__)), 'Data_Sample', 'Sample')
fl_static = os.path.join(DATA_DIR, 'static.c3d')
fl_dynamic = os.path.join(DATA_DIR, 'dynamic.c3d')
settings_file_path = os.path.join(DATA_DIR, 'settings.yml')


def main():

    # 1: load c3d files to dictionary
    sdata = c3d_to_dict(fl_static)
    data = c3d_to_dict(fl_dynamic)

    # 2: load settings from yaml file
    with open(settings_file_path, "r") as yaml_file:
        settings = yaml.safe_load(yaml_file)

    # 3: Setup settings, choose your openOFM version
    settings['version'] = '1.0'                     # todo this could be in the settings.yml?
    settings['data_dir'] = DATA_DIR                 # todo this is weird to be in settings
    settings.update(get_python_settings(settings))  # get processing settings and subject parameters from .yml

    # 4: Create local version of virtual markers present in static trial + add them to dynamic trial
    sdata = create_virtual_markers(sdata, settings)

    filtered_dict = dict(filter(lambda item: 'openOFM' in item[0], sdata['parameters']['PROCESSING'].items()))
    for key, value in filtered_dict.items():
        data['parameters']['PROCESSING'][key] = {}
        data['parameters']['PROCESSING'][key]['value'] = value

    # 5:compute hip, knee and ankle joint center (here we use PIG versions)
    data = hipjointcentrePiG_data(data)
    data = kneejointcenterPiG(data)
    data = anklejointcenterPiG(data)

    # 6: Create dynamic version of virtual markers present in static trial + compute phi and omega
    data = animate_virtual_markers(data, settings)

    # 7: Create virtual segment embedded axes
    data, r, jnt = segments(data, settings['version'])

    # 8: Compute joint angles according to Grood and Suntay method
    data = kinematics(data, r, jnt, settings['version'])

    # 9 plot results
    plot_angles(data=data, plot_title='sample process')


if __name__ == "__main__":
    main()
