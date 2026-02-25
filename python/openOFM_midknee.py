import yaml
import csv
import os
import numpy as np

from OFM.virtual_markers import create_virtual_markers
from python.OFM.virtual_markers import midpoint_joint_center
from utils.utils import c3d_to_dict, find_repo_root, get_python_settings
from OFM.virtual_markers import animate_virtual_markers
from OFM.segments import segments
from OFM.kinematics import kinematics
from plotting.plotting import plot_angles

# path to raw static file, raw dynamic file, and settings file
DATA_DIR = os.path.join(find_repo_root(os.path.dirname(__file__)), 'Josh_Data', 'P06')
fl_static = os.path.join(DATA_DIR, 'static01.c3d')
fl_dynamic = os.path.join(DATA_DIR, 'dynamic01.c3d')
settings_file_path = os.path.join(DATA_DIR, 'settings.yml')

def midknee_process(plot:bool, export:bool, subject:str = None)-> dict:
    """
    Process openOFM data using the middle point of medial and lateral knee
    markers to determine the knee and ankle joint centres.

    :param plot:        True or False - determines if the results are to be plotted
    :param export:      True or False - determines if the results are to be exported
    :param subject:     Subject name, used to label the exported file
    :returns:           Dictionary containing segment DCMs and joint angles
    """

    # 1: load c3d files to dictionary
    sdata = c3d_to_dict(fl_static)
    data = c3d_to_dict(fl_dynamic)

    # 2: load settings from yaml file
    with open(settings_file_path, "r") as yaml_file:
        settings = yaml.safe_load(yaml_file)

    # 3: Setup settings, choose your openOFM version
    settings['version'] = '1.1'
    settings['data_dir'] = DATA_DIR
    settings.update(get_python_settings(settings))  # get processing settings and subject parameters from .yml
    # create empty 'PROCESSING' dict if the .c3d has not been processed at all previously
    if 'PROCESSING' not in sdata['parameters']:
        sdata['parameters']['PROCESSING'] = {}
    if 'PROCESSING' not in data['parameters']:
        data['parameters']['PROCESSING'] = {}

    # 4: Create local version of virtual markers present in static trial + add them to dynamic trial
    # 4.0: Optional: Create joint centers from static markers
    sdata = midpoint_joint_center(sdata, marker1_name='KNE', marker2_name='KNM', midpoint_name='KneeJC')
    sdata = midpoint_joint_center(sdata, marker1_name='ANK', marker2_name='MMA', midpoint_name='AnkleJC')

    sdata = create_virtual_markers(sdata, settings)

    filtered_dict = dict(filter(lambda item: 'openOFM' in item[0], sdata['parameters']['PROCESSING'].items()))
    for key, value in filtered_dict.items():
        data['parameters']['PROCESSING'][key] = {}
        data['parameters']['PROCESSING'][key]['value'] = value

    # 5: Create dynamic version of virtual markers present in static trial + compute phi and omega
    data = animate_virtual_markers(data, settings)

    # 6: Create virtual segment embedded axes
    data, r, jnt = segments(data, settings)

    # 7: Compute joint angles according to Grood and Suntay method
    data = kinematics(data, r, jnt, settings['version'])

    # 8 plot results
    if plot:
        plot_angles(data=data, plot_title='sample process')

    if export:
        out_dir = os.path.join(os.getcwd(), 'processed data')
        os.makedirs(out_dir, exist_ok=True)

        out_file = os.path.join(out_dir, f"{subject}_OFM_results.csv")

        with open(out_file, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=data.keys())
            w.writeheader()
            w.writerow(data)

    return data

def extract_data(ofm_data: dict, angles:bool, axes:bool) -> dict:

    ofm_data = {key: {'line': value} if not isinstance(value, dict) else value
                for key, value in ofm_data.items()}

    data_dict = {}

    if angles:
        sides = ['Left', 'Right']
        joints = ['HFTB', 'FFHF', 'HXFF', 'FFTB']
        axis = ['x', 'y', 'z']

        angle_keys = [f"{s}{j}A_{a}" for s in sides for j in joints for a in axis]

        for key in angle_keys:
            if key in ofm_data:
                data_dict[key] = ofm_data[key]

    if axes:

        sides = ['L', 'R']
        segs = ['TIB', 'HDF', 'FOF', 'HLX']
        nums = ['0', '1', '2', '3']

        axis_keys = [f"{s}{seg}{n}" for s in sides for seg in segs for n in nums]

        for key in axis_keys:
            if key in ofm_data:
                data_dict[key] = ofm_data[key]

    return data_dict

def export_csv(data: dict, subject: str, contains: str):

    out_dir = os.path.join(os.getcwd(), 'processed data')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{subject}_OFM_{contains}.csv")

    first_key = next(iter(data))
    n_frames = data[first_key]['line'].shape[0]

    headers = ['frame']
    column_map = []

    for key, entry in data.items():
        arr = np.asarray(entry['line'])

        if arr.ndim == 1:
            headers.append(key)
            column_map.append((key, None))

        elif arr.ndim == 2:
            for j in range(arr.shape[1]):
                headers.append(f"{key}_{j}")
                column_map.append((key, j))

        else:
            raise ValueError(f"{key}: unsupported shape {arr.shape}")

    with open(out_file, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)

        for i in range(n_frames):
            row = [i]

            for key, j in column_map:
                arr = data[key]['line']
                row.append(arr[i] if j is None else arr[i, j])

            w.writerow(row)


if __name__ == "__main__":

    subject = '061OF' # To process a new participant you also need to change the dir above (line 15)

    data = midknee_process(plot=False, export=False, subject=subject)
    print(data.keys())

    ofm_angles = extract_data(data, angles=True, axes=False)
    export_csv(ofm_angles, subject=subject, contains = 'angles')

    ofm_dcm = extract_data(data, angles = False, axes=True)
    export_csv(ofm_dcm, subject=subject, contains = 'axes')
