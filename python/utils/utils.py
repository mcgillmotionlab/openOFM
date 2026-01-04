import os
import numpy as np
from linear_algebra.linear_algebra import nrmse


def find_repo_root(test, dirs=(".git",), default=None):
    """ Finds full local path to root of code repository"""
    prev, test = None, os.path.abspath(test)
    while prev != test:
        if any(os.path.isdir(os.path.join(test, d)) for d in dirs):
            return test
        prev, test = test, os.path.abspath(os.path.join(test, os.pardir))
    return default or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def c3d_to_dict(fl, verbose=False):
    """ convert c3d file located at fl into dictionary with easily accessible marker data

    Arguments:
        fl      ... str, full path to c3d file
        verbose ... bool, Default = False. If true, information about processing printed to screen
    Returns:
        data    ... dict, c3d file with markers as keys and coordinates as values

    Notes:
        - For details on reading c3d with ezc3d see:
        https://github.com/pyomeca/ezc3d#python-3
    """

    import ezc3d

    if verbose:
        print('converting c3d to dict for: {}'.format(fl))

    # load c3d object
    d = ezc3d.c3d(fl)

    # add all markers to a dictionary
    marker_names = d['parameters']['POINT']['LABELS']['value']  # marker names
    point_data = d['data']['points']  # 4xNxT, where 4 represent the components XYZ1
    data = {}
    for i, marker_name in enumerate(marker_names):
        data[marker_name] = point_data[0:3, i, :].T  # we only want XYZ components in N X 3 format

    # add analog data to dictionary
    analog_names = d['parameters']['ANALOG']['LABELS']['value']
    analog_data = d['data']['analogs']
    for i, analog_name in enumerate(analog_names):
        data[analog_name] = analog_data[0:3, i, :].T  # we only want XYZ components in N X 3 format

    # add meta information
    if 'parameters' in d.keys():
        data['parameters'] = {}
        params = list(d['parameters'].keys())
        for param in params:
            data['parameters'][param] = d['parameters'][param]

    # header
    if 'header' in d.keys():
        data['header'] = {}
        headers = list(d['header'].keys())
        for header in headers:
            data['header'][param] = d['header'][header]

    return data


def addchannelsgs(data, KIN):
    """ helper function to add all the computed data to the data dict"""

    mappings = [
        ('HFTBA', 'AnkleOFM', ('flx', 'tw', 'abd')),
        ('FFHFA', 'MidFoot',  ('flx', 'abd', 'tw')),
        ('HXFFA', 'MTP',      ('flx', 'abd', 'tw')),
        ('TIBA',  'TibiaLab', ('flx', 'abd', 'tw')),
        ('FFTBA', 'FFTBA',    ('flx', 'tw', 'abd'))
    ]

    for side in ['Right', 'Left']:
        for d_name, k_name, src_comps in mappings:
            for axis, comp in zip('xyz', src_comps):
                data[f"{side}{d_name}_{axis}"] = KIN[f"{side}{k_name}"][comp]

    return data


def getDir(data, ch=None):
    """ get direction of movement based on marker ch"""

    # use PiG pelvis marker or inputted channel
    if ch is None:
        if 'RPSI' in data:
            RPSI = data['RPSI']
            LPSI = data['LPSI']
            vec = (RPSI + LPSI) / 2
        elif 'SACR' in data:
            vec = data['SACR']
        elif 'RPCA' in data:
            vec = data['RPCA']
        else:
            raise ValueError
    else:
        vec = data[ch]

    # Determine if most of motion is along global X or Y
    X = abs(vec[0, 0] - vec[-1, 0])
    Y = abs(vec[0, 1] - vec[-1, 1])

    if Y > X:  # moving along Y
        axis = 'J'
        dim = 1
    else:  # moving along X
        axis = 'I'
        dim = 0

    # Determine which direction along the known axis the person is travelling
    vec = vec[:, dim]
    indx = ~np.isnan(vec)
    vec = vec[indx]

    if vec[0] > vec[-1]:
        direction = 'neg'  # negative slope
    else:
        direction = 'pos'

    # todo implement z direction

    walkDir = axis + direction

    return walkDir
def getDir(data, ch=None):
    """ get direction of movement based on marker ch"""

    # Determine Vector Source
    if ch:
        vec = data[ch]
    elif 'RPSI' in data:
        vec = (data['RPSI'] + data['LPSI']) / 2
    else:
        vec = data.get('SACR', data.get('RPCA'))
        if vec is None: raise ValueError

    # Determine Dominant Axis (Global X vs Y)
    dim = np.argmax(np.abs(vec[-1, :2] - vec[0, :2]))
    
    # Determine Direction (Pos vs Neg)
    v_clean = vec[:, dim]
    v_clean = v_clean[~np.isnan(v_clean)]

    axis_char = ['I', 'J'][dim]
    slope_str = 'neg' if v_clean[0] > v_clean[-1] else 'pos'

    # todo implement z direction
    return axis_char + slope_str

def getDirStat(data, ch=None):
    """ get direction of standing based on foot markers"""

    prox = data['RPCA']
    dist = data['RD1M']

    # Determine if foot is oriented along global X or Y
    X = abs(prox[0, 0] - dist[-1, 0])
    Y = abs(prox[0, 1] - dist[-1, 1])

    if Y > X:  # standing facing Y
        axis = 'J'
        dim = 1
    else:  # standing facing X
        axis = 'I'
        dim = 0

    # todo implement z direction

    # Determine which direction along the known axis the person is travelling
    vec = dist[:, dim] - prox[:, dim]
    indx = ~np.isnan(vec)
    vec = np.average(vec[indx])

    if vec < 0:
        direction = 'neg'  # toe marker is "behind" heel marker
    else:
        direction = 'pos'

    standDir = axis + direction

    return standDir


def get_data(settings):
    # extract settings
    trial_type = settings['trial_type']
    file_name = settings['file_name']
    version = settings['version']

    if trial_type not in ['static', 'dynamic']:
        raise IOError('Trial type {} incorrect, must be "static" or "dynamic".'.format(trial_type))

    # 1.0 get path to c3d files
    ROOT_DIR = find_repo_root(os.path.dirname(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, settings['data_dir'])

    # 2.0 Load data and compute ofm

    # get path to files
    fl = os.path.join(DATA_DIR, file_name)
    print('Processing {}'.format(trial_type), 'file {}'.format(fl), 'with openOFM version {}.'.format(version))

    # 2.1 load c3d files to dictionary
    data = c3d_to_dict(fl)

    # set settings from data if not already present
    if 'processing' not in settings:
        settings['processing'] = dict(LHindFootFlat=data['parameters']['PROCESSING']['LHindFootFlat']['value'][0].astype(int),
                                      RHindFootFlat=data['parameters']['PROCESSING']['RHindFootFlat']['value'][0].astype(int),
                                      LUseFloorFF=data['parameters']['PROCESSING']['LUseFloorFF']['value'][0].astype(int),
                                      RUseFloorFF=data['parameters']['PROCESSING']['RUseFloorFF']['value'][0].astype(int),
                                      )

    # create empty 'PROCESSING' dict if the .c3d has not been processed at all previously
    if 'PROCESSING' not in data['parameters']:
        data['parameters']['PROCESSING'] = {}

    if trial_type == 'dynamic':
        fl = os.path.join(DATA_DIR, 'parameters.txt')
        with open(fl, 'r') as f:
            # Read the contents of the file into a list
            lines = f.readlines()
            # Loop through the list of lines
            for line in lines:
                # Split the line into key-value pairs,removing $ from each line
                key, value = line.strip('$').split('=')
                key = key.strip()
                # Store the key-value pairs in the dictionary
                data['parameters']['PROCESSING'][key] = {}
                data['parameters']['PROCESSING'][key]['value'] = float(value)

        if settings['use_settings']:
            print('Loading anthropometric values from settings dictionary')
            data['parameters']['PROCESSING']['MarkerDiameter'] = {}
            data['parameters']['PROCESSING']['MarkerDiameter']['value'] = settings['subject_params']['MarkerDiameter']
            if settings['version'] == '1.0':
                data['parameters']['PROCESSING']['InterAsisDistance']['value'] = settings['subject_params']['InterAsisDistance']
                data['parameters']['PROCESSING']['RLegLength']['value'] = settings['subject_params']['RLegLength']
                data['parameters']['PROCESSING']['LLegLength']['value'] = settings['subject_params']['LLegLength']
                data['parameters']['PROCESSING']['RKneeWidth']['value'] = settings['subject_params']['RKneeWidth']
                data['parameters']['PROCESSING']['LKneeWidth']['value'] = settings['subject_params']['LKneeWidth']
                data['parameters']['PROCESSING']['RAnkleWidth']['value'] = settings['subject_params']['RAnkleWidth']
                data['parameters']['PROCESSING']['LAnkleWidth']['value'] = settings['subject_params']['LAnkleWidth']
                data['parameters']['PROCESSING']['RThighRotation']['value'] = settings['subject_params'][
                    'RThighRotation']
                data['parameters']['PROCESSING']['LThighRotation']['value'] = settings['subject_params'][
                    'LThighRotation']
                data['parameters']['PROCESSING']['RShankRotation']['value'] = settings['subject_params'][
                    'RShankRotation']
                data['parameters']['PROCESSING']['LShankRotation']['value'] = settings['subject_params'][
                    'LShankRotation']
        else:
            print('Loading anthropometric values from {}'.format(fl))

    return data, settings


def set_data(data, settings):
    # 1.0 get path to c3d files
    ROOT_DIR = find_repo_root(os.path.dirname(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, settings['data_dir'])

    # create new dictionary with only openOFM processing parameters
    filtered_dict = dict(filter(lambda item: 'openOFM' in item[0], data['parameters']['PROCESSING'].items()))

    fl = os.path.join(DATA_DIR, 'parameters.txt')
    with open(fl, 'w') as f:
        print('Saving computed parameters to {}'.format(fl))
        # print each parameter value on a new line of a temporary .txt file
        for key, value in filtered_dict.items():
            print(key, '=', value, file=f)


def is_nexus():
    """ check if user is running openOFM via Vicon Nexus"""
    import warnings
    try:
        # check if vicon api is installed
        from viconnexusapi import ViconNexus

        try:
            # check if Nexus is open, and api is installed
            vicon = ViconNexus.ViconNexus()

            try:
                # check if a trial with a subject is selected in Nexus
                vicon.GetSubjectNames()[0]
                nexus = True

            except IndexError:
                warnings.warn('To use Vicon Nexus, select the trial in Nexus you wish to process.')
                nexus = False

        except IOError:
            warnings.warn('To use Vicon Nexus, open Nexus and select the  trial you wish to process')
            nexus = False

    except ModuleNotFoundError:
        nexus = False

    if nexus:
        print('running openOFM via Vicon Nexus...')
    else:
        print('running openOFM via python...')

    return nexus


def get_settings():

    import warnings
    try:
        # check if vicon api is installed
        from viconnexusapi import ViconNexus

        try:
            # check if Nexus is open, and api is installed
            vicon = ViconNexus.ViconNexus()

            try:
                # check if a trial with a subject is selected in Nexus
                vicon.GetSubjectNames()[0]
                nexus = True

            except IndexError:
                warnings.warn('To use Vicon Nexus, select the trial in Nexus you wish to process.')
                nexus = False

        except IOError:
            warnings.warn('To use Vicon Nexus, open Nexus and select the  trial you wish to process')
            nexus = False

    except ModuleNotFoundError:
        nexus = False

    if nexus:
        import sys
        settings = dict(nexus=nexus,
                        version=sys.argv[1],
                        )
    else:
        settings = dict()

    return settings


def get_python_settings(args):
    """ helper method to load appropriate files"""
    import yaml

    # extract arguments to dictionary
    root_dir = find_repo_root(os.path.dirname(__file__))
    data_dir = os.path.join(root_dir, args['data_dir'])
    yaml_file_path = os.path.join(data_dir, 'settings.yml')
    with open(yaml_file_path, "r") as yaml_file:
        python_settings = yaml.safe_load(yaml_file)

    return python_settings


def make_plot_title(settings):
    """ helper function to generate a plot title"""
    subject = os.path.join(settings['data_dir'], settings['file_name'])
    plot_title = "{} LHFF({}) RHFF({}) LUseFloor({}) RUseFloor({})".format(
        subject, str(settings['processing']['LHindFootFlat']), str(settings['processing']['RHindFootFlat']),
        str(settings['processing']['LUseFloorFF']), str(settings['processing']['RUseFloorFF'])
    )
    # plot_title = "plot"
    return plot_title

def get_nrmse(data_raw, data_processed):
    sides = ['Right', 'Left']
    joints = ['TIBA', 'HFTBA', 'FFTBA', 'FFHFA', 'HXFFA']

    for side in sides:
        s = side[0]
        for joint in joints:
            axes = ['x', 'y'] if joint == 'HXFFA' else ['x', 'y', 'z']
            
            for i, ax in enumerate(axes):
                val = nrmse(data_processed[s + joint][:, i], data_raw[side + joint + '_' + ax])
                data_raw[f'nrmse{side}{joint}_{ax}'] = str(round(val, 4))

        # compare metrics (arch height)
        data_raw['nrmse' + s + 'ArchHeightIndex'] = str(
            round(nrmse(data_processed[s + 'ArchHeightIndex'][:, 2], data_raw[s + 'ArchHeightIndex']), 4))
            
        data_raw['nrmse' + s + 'ArchHeight'] = str(
            round(nrmse(data_processed[s + 'ArchHeight'][:, 2], data_raw[s + 'ArchHeight'][:, 2]), 4))

    return data_raw