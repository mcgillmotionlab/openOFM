import os
import yaml

from openofm import OFM



# set paths
base_dir = os.path.dirname(os.path.abspath('.'))
DATA_DIR = os.path.join(base_dir, 'Data_Sample', 'Sample')
static_file_path = os.path.join(DATA_DIR, 'static.c3d')
dynamic_file_path = os.path.join(DATA_DIR, 'dynamic.c3d')
subject_parameters_file_path = os.path.join(DATA_DIR, 'subject_measurements.yml')
process_parameters_file_path = os.path.join(DATA_DIR, 'process_options.yml')




# Initialize ofm object
ofm = OFM(version='1.1')

# load required parameters
ofm.load_subject_parameters(subject_parameters_file_path)
ofm.load_processing_parameters(process_parameters_file_path)

# process static trial
#todo: do we want to separate load and process?
ofm.load_static_data(filepath=static_file_path)
ofm.process_static_trial()

# # Step 3: process a dynamic trial
#todo: maybe users should compute joint centers on the static trials always and then pass the virtual marker to the dynamic
#todo: update code to allow users to write their custom joint center code without messing with our methods. Show an example
#todo: consider if joint center stuff should be done on the static trial?
ofm.compute_hip_joint_center(method='pig')
ofm.compute_knee_joint_center(method='pig')
ofm.compute_ankle_joint_center(method='pig')

#todo: do we want to separate load and process?
ofm.load_dynamic_data(filepath=dynamic_file_path)
ofm.process_dynamic_trial()  # processing options would have been set during static set up, any reason to change?

ofm.plot_angles(plot_title='sample process')