import os
from typing import Any
import numpy as np
import requests
from pathlib import Path

from openofm.linear_algebra.linear_algebra import nrmse


API_BASE = "https://api.github.com/repos/mcgillmotionlab/openOFM/contents"


def _download_file(url, out_path):
    r = requests.get(url)
    r.raise_for_status()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)


def _fetch_folder(folder, out_dir):
    api_url = f"{API_BASE}/{folder}"
    r = requests.get(api_url)
    r.raise_for_status()

    items = r.json()

    for item in items:
        if item["type"] == "file":
            out_path = Path(out_dir) / item["name"]
            _download_file(item["download_url"], out_path)

        elif item["type"] == "dir":
            _fetch_folder(f"{folder}/{item['name']}", Path(out_dir) / item["name"])


def fetch_dataset(name="Data_Sample", cache_dir="~/.openofm"):
    cache_dir = Path(cache_dir).expanduser()
    target = cache_dir / name

    if target.exists():
        return target

    _fetch_folder(name, target)
    return target


def extract_value(v: Any) -> Any:
    """Extract the ``'value'`` field from a parameter dict, or return *v* unchanged.

    Parameters
    ----------
    v : Any
        Raw parameter entry, typically ``{'value': ...}`` from a C3D
        ``parameters`` block, or any plain value.

    Returns
    -------
    Any
        ``v['value']`` when *v* is a dict with a ``'value'`` key,
        otherwise *v* itself.
    """
    if isinstance(v, dict) and 'value' in v:
        return v['value']
    return v

def find_repo_root(
    test: str,
    dirs: tuple[str, ...] = (".git",),
    default: str | None = None,
) -> str:
    """Find the full local path to the root of the code repository.

    Parameters
    ----------
    test : str
        Starting path for the upward search.
    dirs : tuple of str, optional
        Marker directory names that identify the repo root (default ``('.git',)``).
    default : str or None, optional
        Fallback path when no marker is found.  Defaults to two levels above
        this file.

    Returns
    -------
    str
        Absolute path to the repository root.
    """
    prev, test = None, os.path.abspath(test)
    while prev != test:
        if any(os.path.isdir(os.path.join(test, d)) for d in dirs):
            return test
        prev, test = test, os.path.abspath(os.path.join(test, os.pardir))
    return default or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def c3d_to_dict(fl: str, verbose: bool = False) -> dict:
    """Convert a C3D file to a dictionary with easily accessible marker data.

    Parameters
    ----------
    fl : str
        Full path to the C3D file.
    verbose : bool, optional
        If ``True``, print progress information during loading.  Default ``False``.

    Returns
    -------
    dict
        Dictionary with marker names as keys and ``(N, 3)`` coordinate arrays
        as values.  Also contains ``'parameters'`` and ``'header'`` sub-dicts.

    Notes
    -----
    For details on reading C3D files with ezc3d see
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


def set_params(side: str, marker_lcl_av: np.ndarray, data: dict, marker: str) -> None:
    """Store averaged local-coordinate virtual-marker position in the C3D parameter dict.

    Parameters
    ----------
    side : str
        Body side identifier, ``'R'`` or ``'L'``.
    marker_lcl_av : np.ndarray
        Shape ``(1, 3)`` array with the averaged X, Y, Z local coordinates.
    data : dict
        Trial data dictionary whose ``parameters['PROCESSING']`` block is updated
        in-place.
    marker : str
        Marker name suffix, e.g. ``'D1M0'`` → keys ``'%RD1M0X_openOFM'`` …
    """
    data['parameters']['PROCESSING']['%' + side + marker + 'X_openOFM'] = marker_lcl_av[0, 0]
    data['parameters']['PROCESSING']['%' + side + marker + 'Y_openOFM'] = marker_lcl_av[0, 1]
    data['parameters']['PROCESSING']['%' + side + marker + 'Z_openOFM'] = marker_lcl_av[0, 2]


def addchannelsgs(data: dict, KIN: dict) -> dict:
    """Add all computed kinematic channels to the trial data dictionary.

    Parameters
    ----------
    data : dict
        Trial data dictionary, updated in-place.
    KIN : dict
        Computed joint angles keyed by joint/segment name.

    Returns
    -------
    dict
        Updated *data* dictionary.
    """
    sides = ['Right', 'Left']
    for side in sides:
        data[side + 'HFTBA_x'] = KIN[side + 'AnkleOFM']['flx']
        data[side + 'HFTBA_y'] = KIN[side + 'AnkleOFM']['tw']
        data[side + 'HFTBA_z'] = KIN[side + 'AnkleOFM']['abd']

        data[side + 'FFHFA_x'] = KIN[side + 'MidFoot']['flx']
        data[side + 'FFHFA_y'] = KIN[side + 'MidFoot']['abd']
        data[side + 'FFHFA_z'] = KIN[side + 'MidFoot']['tw']

        data[side + 'HXFFA_x'] = KIN[side + 'MTP']['flx']
        data[side + 'HXFFA_y'] = KIN[side + 'MTP']['abd']
        data[side + 'HXFFA_z'] = KIN[side + 'MTP']['tw']

        data[side + 'TIBA_x'] = KIN[side + 'TibiaLab']['flx']
        data[side + 'TIBA_y'] = KIN[side + 'TibiaLab']['abd']
        data[side + 'TIBA_z'] = KIN[side + 'TibiaLab']['tw']

        data[side + 'FFTBA_x'] = KIN[side + 'FFTBA']['flx']
        data[side + 'FFTBA_y'] = KIN[side + 'FFTBA']['tw']
        data[side + 'FFTBA_z'] = KIN[side + 'FFTBA']['abd']

        data[side + 'WFTBA_x'] = KIN[side + 'WFTBA']['flx']
        data[side + 'WFTBA_y'] = KIN[side + 'WFTBA']['tw']
        data[side + 'WFTBA_z'] = KIN[side + 'WFTBA']['abd']

    return data


def getDir(data: dict, ch: str | None = None) -> str:
    """Determine the direction of movement from a reference marker trajectory.

    Parameters
    ----------
    data : dict
        Trial data dictionary containing marker arrays.
    ch : str or None, optional
        Channel name to use as reference.  When ``None`` the function falls
        back to ``'RPSI'`` / ``'SACR'`` / ``'RPCA'`` in that order.

    Returns
    -------
    str
        Walk direction string: one of ``'Ipos'``, ``'Ineg'``, ``'Jpos'``,
        ``'Jneg'``.
    """

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


def getDirStat(data: dict, ch: str | None = None) -> str:
    """Determine the direction of standing from foot marker positions.

    Parameters
    ----------
    data : dict
        Trial data dictionary containing at least ``'RPCA'`` and ``'RD1M'``
        marker arrays.
    ch : str or None, optional
        Unused.  Reserved for future extension.

    Returns
    -------
    str
        Standing direction string: one of ``'Ipos'``, ``'Ineg'``, ``'Jpos'``,
        ``'Jneg'``.
    """

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


def get_data(settings: dict) -> tuple[dict, dict]:
    """Load a C3D trial file and populate processing settings.

    Parameters
    ----------
    settings : dict
        Processing settings.  Required keys: ``'trial_type'``, ``'file_name'``,
        ``'version'``, ``'data_dir'``.  Optional: ``'processing'``,
        ``'use_settings'``, ``'subject_params'``.

    Returns
    -------
    data : dict
        Loaded C3D data dictionary with parameters block populated.
    settings : dict
        Updated settings dictionary with ``'processing'`` sub-dict added.
    """
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


def set_data(data: dict, settings: dict) -> None:
    """Write openOFM processing parameters to ``parameters.txt``.

    Parameters
    ----------
    data : dict
        Trial data dictionary whose ``parameters['PROCESSING']`` block
        contains the openOFM parameters to persist.
    settings : dict
        Processing settings.  Required key: ``'data_dir'``.
    """
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


def is_nexus() -> bool:
    """Check whether openOFM is being invoked from inside Vicon Nexus.

    Returns
    -------
    bool
        ``True`` when a Nexus session with an active trial is detected,
        ``False`` otherwise.
    """
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


def get_settings() -> dict:
    """Build a minimal settings dictionary for Nexus or standalone Python mode.

    Returns
    -------
    dict
        Settings dict containing ``'nexus'`` (bool) and, when running inside
        Vicon Nexus, ``'version'`` extracted from ``sys.argv``.
    """
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


def get_python_settings(args: dict) -> dict:
    """Load subject-measurement settings from a YAML file.

    Parameters
    ----------
    args : dict
        Argument dictionary that must contain ``'data_dir'``.

    Returns
    -------
    dict
        Contents of the ``subject_measurements.yml`` file found in
        ``<repo_root>/<data_dir>/``.
    """
    import yaml

    # extract arguments to dictionary
    root_dir = find_repo_root(os.path.dirname(__file__))
    data_dir = os.path.join(root_dir, args['data_dir'])
    yaml_file_path = os.path.join(data_dir, 'subject_measurements.yml')
    with open(yaml_file_path, "r") as yaml_file:
        python_settings = yaml.safe_load(yaml_file)

    return python_settings


def make_plot_title(settings: dict) -> str:
    """Generate a descriptive plot title from trial settings.

    Parameters
    ----------
    settings : dict
        Must contain keys ``'data_dir'``, ``'file_name'``, and
        ``'processing'`` (with sub-keys ``'LHindFootFlat'``,
        ``'RHindFootFlat'``, ``'LUseFloorFF'``, ``'RUseFloorFF'``).

    Returns
    -------
    str
        Human-readable title string.
    """
    subject = os.path.join(settings['data_dir'], settings['file_name'])
    plot_title = "{} LHFF({}) RHFF({}) LUseFloor({}) RUseFloor({})".format(
        subject, str(settings['processing']['LHindFootFlat']), str(settings['processing']['RHindFootFlat']),
        str(settings['processing']['LUseFloorFF']), str(settings['processing']['RUseFloorFF'])
    )
    # plot_title = "plot"
    return plot_title

def get_nrmse(data_raw: dict, data_processed: dict) -> dict:
    """Compute NRMSE between openOFM and Vicon-processed kinematic channels.

    Parameters
    ----------
    data_raw : dict
        openOFM-processed trial data.
    data_processed : dict
        Vicon-processed reference data for comparison.

    Returns
    -------
    dict
        *data_raw* updated in-place with ``'nrmse<side><channel>'`` string
        entries for each kinematic channel.
    """
    sides = ['Right', 'Left']
    for side in sides:
        s = side[0]
        data_raw['nrmse' + side + 'TIBA_x'] = str(round(nrmse(data_processed[s + 'TIBA'][:, 0], data_raw[side + 'TIBA_x']), 4))
        data_raw['nrmse' + side + 'TIBA_y'] = str(round(nrmse(data_processed[s + 'TIBA'][:, 1], data_raw[side + 'TIBA_y']), 4))
        data_raw['nrmse' + side + 'TIBA_z'] = str(round(nrmse(data_processed[s + 'TIBA'][:, 2], data_raw[side + 'TIBA_z']), 4))

        data_raw['nrmse' + side + 'HFTBA_x'] = str(round(nrmse(data_processed[s + 'HFTBA'][:, 0], data_raw[side + 'HFTBA_x']), 4))
        data_raw['nrmse' + side + 'HFTBA_y'] = str(round(nrmse(data_processed[s + 'HFTBA'][:, 1], data_raw[side + 'HFTBA_y']), 4))
        data_raw['nrmse' + side + 'HFTBA_z'] = str(round(nrmse(data_processed[s + 'HFTBA'][:, 2], data_raw[side + 'HFTBA_z']), 4))

        data_raw['nrmse' + side + 'FFTBA_x'] = str(round(nrmse(data_processed[s + 'FFTBA'][:, 0], data_raw[side + 'FFTBA_x']), 4))
        data_raw['nrmse' + side + 'FFTBA_y'] = str(round(nrmse(data_processed[s + 'FFTBA'][:, 1], data_raw[side + 'FFTBA_y']), 4))
        data_raw['nrmse' + side + 'FFTBA_z'] = str(round(nrmse(data_processed[s + 'FFTBA'][:, 2], data_raw[side + 'FFTBA_z']), 4))

        data_raw['nrmse' + side + 'FFHFA_x'] = str(round(nrmse(data_processed[s + 'FFHFA'][:, 0], data_raw[side + 'FFHFA_x']), 4))
        data_raw['nrmse' + side + 'FFHFA_y'] = str(round(nrmse(data_processed[s + 'FFHFA'][:, 1], data_raw[side + 'FFHFA_y']), 4))
        data_raw['nrmse' + side + 'FFHFA_z'] = str(round(nrmse(data_processed[s + 'FFHFA'][:, 2], data_raw[side + 'FFHFA_z']), 4))

        data_raw['nrmse' + side + 'HXFFA_x'] = str(round(nrmse(data_processed[s + 'HXFFA'][:, 0], data_raw[side + 'HXFFA_x']), 4))
        data_raw['nrmse' + side + 'HXFFA_y'] = str(round(nrmse(data_processed[s + 'HXFFA'][:, 1], data_raw[side + 'HXFFA_y']), 4))


        # compare metrics (arch height)
        data_raw['nrmse' + s + 'ArchHeightIndex'] = str(
            round(nrmse(data_processed[s + 'ArchHeightIndex'][:, 2], data_raw[s + 'ArchHeightIndex']), 4))
        data_raw['nrmse' + s + 'ArchHeight'] = str(
            round(nrmse(data_processed[s + 'ArchHeight'][:, 2], data_raw[s + 'ArchHeight'][:, 2]), 4))

    return data_raw



