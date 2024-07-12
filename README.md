# openOFM
Code repository for the openOFM project. See manuscript "openOFM: an open-source implementation of the Oxford 
multi-segment foot model" for full mathematical details and further instructions.

## Running in Python

### Environment setup
Python users must set up an appropriate environment to run openOFM.
The following steps assume the user has installed the Anaconda or Mini-
conda python distribution and has launched a terminal (Mac OS/Linux) or
command prompt (PC). Similar commands can be run via Python IDEs.
1. Create environment: ``conda create --name openOFM python=3.9 -y``
2. Activate environment: ``conda activate openOFM``
3. Change directory to python subdirectory of the openOFM repository:
``cd ...\openOFM\python``
4. Install packages: ``conda install --y --file requirements.txt``
5. If the ezc3d package does not install, add conda-forge to channels before
trying step 4 again: ``conda config --add channels conda-forge``

### Running the openOFM Python scripts
Users may run the Python scripts using two main approaches.
First, users may run the ``openOFM_static.py`` and ``openOFM_dynamic.py``
files directly (also used by Nexus). Running these files without any arguments
will default to processing the data within the ``Data_Sample`` folder for version
1.0. Users may append additional flags to modify settings. For example, the
following command allows users to process a static trial using version 1.1 and
the subject parameters defined in a settings.yml file:
``python openOFM_static.py --version 1.1 --use_settings``

When processing data through the openOFM static or openOFM dynamic
pipelines, the following arguments can be used:
1. ``version`` can be set to “1.0” or “1.1”.
2. ``data_dir`` is the name of subject folder relative to the root
3. ``file_name`` is the name of the .c3d to process
4. ``use_settings`` controls whether to use the subject parameters and 
   processing settings from a .c3d file or a settings.yml file defined by the user
5. ``make_plot`` (``openOFM_dynamic.py`` only). Allows users to generate a
plot of results.

Options can be reviewed via the command: ``python openOFM_static.py --h``
and ``python openOFM_dynamic.py --h``

Second, users may run the ``openOFM_sample_process.py``. This approach
may be more appropriate for users/developers wishing to integrate openOFM
into their analysis or modify computations.

### Validating the openOFM code
An additional ``openOFM_validate.py`` script compares openOFM python
(version 1.0) and Vicon implementations using the sample data provided.
Running this script will display OFM kinematics for both implementations.

## Running in Matlab

Although officially unsupported, the openOFM is available for use in
Matlab. The following steps assume Matlab is installed with a valid lincense:
1. Download the openOFM repository to a location of your choice
2. Change the working directory to the Matlab subfolder of the repository
3. Add the Matlab folder and its subfolders to the Matlab path
4. Run the ``openOFM process.m`` or ``openOFM_validate.m`` script

### openOFM process.m
1. Set the desired version ’1.0’ or ’1.1’ on line 8
2. If anthropometric measures are missing from the .c3d files, set set-
tings.manualAnthro (line 9) to True, and add the measure to section
2.2 (line 30)
3. Select subject folder when prompted, for example MA 00 in folder
``Data Sample``

Note, the ``openOFM_process.m`` should be modified for use with a user’s own
data as it defaults to running version 1.1 on the Data_Sample participant
with placeholder values in the settings.