#imports
import os
from openOFM import openOFM


# set paths
base_dir = os.path.dirname(os.path.abspath('.'))
DATA_DIR = os.path.join(base_dir, 'Data_Sample', 'Sample')
fl_static = os.path.join(DATA_DIR, 'static.c3d')
fl_dynamic = os.path.join(DATA_DIR, 'dynamic.c3d')
subject_measurements = os.path.join(DATA_DIR, 'subject_measurements.yml')
process_options = os.path.join(DATA_DIR, 'process_options.yml')

# Step 1: Initialize object
# Initialize object to use version 1.1 (not selecting a version at initialization leads to an error).
# todo: allow users to set up static trial immediately
# todo: produce a cute message after initialization
ofm = openOFM(version='1.1')

# Step 2: process static trial
ofm.load_static_file(filepath=fl_static) # load static trial stored as c3d
ofm.load_subject_measurements(filepath=subject_measurements) # load subject measurements stored in a yaml file
ofm.process_static_trial(process_options=process_options) # process static trial

# Step 3: process a dynamic trial
#todo: maybe users should compute joint centers on the static trials always and then pass the virtual marker to the dynamic
#todo: update code to allow users to write their custom joint center code without messing with our methods. Show an example
#todo: consider if joint center stuff should be done on the static trial?
ofm.load_dynamic_file(filepath=fl_dynamic)

ofm.compute_hip_joint_center(method='pig')
ofm.compute_knee_joint_center(method='pig')
ofm.compute_ankle_joint_center(method='pig')

ofm.process_dynamic_file()  # processing options would have been set during static set up, any reason to change?

ofm.plot_angles(plot_title='sample process')