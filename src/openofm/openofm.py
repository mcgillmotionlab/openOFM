import os
from collections.abc import Callable
from typing import Union

import yaml

from .OFM.virtual_markers import create_virtual_markers, animate_virtual_markers
from .OFM.segments import segments
from .OFM.kinematics import kinematics
from .PiG.pig import hipjointcentrePiG, kneejointcenterPiG, anklejointcenterPiG
from .plotting.plotting import plot_angles
from .utils.utils import c3d_to_dict, fetch_dataset

#todo: should we split stuff about collection session (e.g. marker diameter) from subject_measurements (e.g. knee width)?
#todo: initialize with version 1.0 instead of None and raising an error?



class openOFM:


    DEFAULT_PROCESSING_OPTIONS = {
        'RUseFloorFF': False,
        'LUseFloorFF': False,
        'RHindFootFlat': True,
        'LHindFootFlat': True,
    }

    HJCMethod = Union[str, Callable[[dict], dict]]
    KJCMethod = Union[str, Callable[[dict], dict]]
    AJCMethod = Union[str, Callable[[dict], dict]]

    def __init__(self, static_file: str | None = None, dynamic_file: str | None = None,
                 subject_measurements: dict | None = None, process_options: dict | None = None,
                 version: str | None = None,) -> None:
        """Initialise an openOFM processing session.

        Parameters
        ----------
        static_file : str or None, optional
            Path to the static C3D file.
        dynamic_file : str or None, optional
            Path to the dynamic C3D file.
        subject_measurements : dict or None, optional
            Subject anthropometric parameters (e.g. ankle width, knee width).
        process_options : dict or None, optional
            Processing flags.
        version : str or None, optional
            openOFM model version. Options 1.0 or 1.1.
        """

        # version must be set
        if version is None:
            raise ValueError("version must be specified at initialization")

        # file inputs
        self.static_file = static_file
        self.dynamic_file = dynamic_file

        self.subject_measurements = subject_measurements

        # configuration
        self.process_options = process_options
        self.version=version

        # bookkeeping
        self.is_static_processed = False
        self.is_dynamic_processed = False

        self.static_data = None
        self.dynamic_data = None
        self.ofm_parameters = None


    def load_static_file(self, filepath: str | None = None) -> None:
        """Load static trial data from a C3D file.

        Parameters
        ----------
        filepath : str or None, optional
            Path to the static C3D file.  When provided, overrides
            ``self.static_file``.
        """

        if filepath is not None:
            self.static_file = filepath

        if self.static_file is None:
            raise ValueError("static file must be set before loading if not using an argument")

        if not os.path.exists(self.static_file):
            raise FileNotFoundError('Static file {} not found'.format(self.static_file))

        self.static_data = c3d_to_dict(self.static_file)


    def load_dynamic_file(self, filepath: str | None = None) -> None:
        """Load dynamic trial data from a C3D file.

        Parameters
        ----------
        filepath : str or None, optional
            Path to the dynamic C3D file.  When provided, overrides
            ``self.dynamic_file``.
        """

        if filepath is not None:
            self.dynamic_file = filepath

        if self.dynamic_file is None:
            raise ValueError("dynamic file must be set before loading if not using an argument")

        if not os.path.exists(self.dynamic_file):
            raise FileNotFoundError('Dynamic file {} not found'.format(self.dynamic_file))

        self.dynamic_data = c3d_to_dict(self.dynamic_file)

    def load_subject_measurements(self, filepath: str) -> None:
        """Load subject anthropometric measurements from a YAML file.

        Parameters
        ----------
        filepath : str
            Path to ``subject_measurements.yml``.
        """

        if not os.path.exists(filepath):
            raise FileNotFoundError('File {} not found'.format(filepath))

        with open(filepath, 'r') as f:
            self.subject_measurements = yaml.safe_load(f)


    def process_static_trial(self, process_options: dict | None = None) -> None:
        """Run the static calibration pipeline to compute virtual markers.

        Parameters
        ----------
        process_options : dict or None, optional
            Processing flags.  Falls back to
            :attr:`DEFAULT_PROCESSING_OPTIONS` when ``None``.
        """


        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        if self.subject_measurements is None:
            raise ValueError('Subject measurements not loaded. Call load_subject_measurements() first.')

        if self.process_options is None:
            self.process_options = self.DEFAULT_PROCESSING_OPTIONS.copy()
        else:
            self.process_options = process_options

        self.static_data, self.ofm_parameters = create_virtual_markers(self.static_data, self.process_options, self.version)

    def compute_hip_joint_center(self, method: HJCMethod = 'pig') -> None:
        """Compute the hip joint centre and store it in ``self.static_data``.

        Parameters
        ----------
        method : str or callable, optional
            Method to use.  ``'pig'`` (default) uses the Plug-in Gait
            Davis et al. (1991) approach.  A callable receives
            ``self.static_data`` and must return the updated data dict.
        """
        #todo: allow upper case PIG or mixed PiG to still work
        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        if method == 'pig':
            self.static_data = hipjointcentrePiG(self.static_data)
        elif callable(method):
            self.static_data = method(self.static_data)
        else:
            raise ValueError("Unknown method '{}'. Use 'pig' or provide a callable function.".format(method))


    def compute_knee_joint_center(self, method: KJCMethod = 'pig') -> None:
        """Compute the knee joint centre and store it in ``self.static_data``.

        Parameters
        ----------
        method : str or callable, optional
            Method to use.  ``'pig'`` (default) uses the Plug-in Gait chord
            method.  A callable receives ``self.static_data`` and must return
            the updated data dict.
        """
        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        if method == 'pig':
            self.static_data = kneejointcenterPiG(self.static_data)
        elif callable(method):
            self.static_data = method(self.static_data)
        else:
            raise ValueError("Unknown method '{}'. Use 'pig' or provide a callable function.".format(method))

    def compute_ankle_joint_center(self, method: AJCMethod = 'pig') -> None:
        """Compute the ankle joint centre and store it in ``self.static_data``.

        Parameters
        ----------
        method : str or callable, optional
            Method to use.  ``'pig'`` (default) uses the Plug-in Gait chord
            method.  A callable receives ``self.static_data`` and must return
            the updated data dict.
        """
        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        if method == 'pig':
            self.static_data = anklejointcenterPiG(self.static_data)
        elif callable(method):
            self.static_data = method(self.static_data)
        else:
            raise ValueError("Unknown method '{}'. Use 'pig' or provide a callable function.".format(method)
            )

    def process_dynamic_file(self) -> None:
        """Run the full dynamic processing pipeline (animate → segments → kinematics)."""

        self.dynamic_data = animate_virtual_markers(self.dynamic_data, self.process_options, self.ofm_parameters,
                                                    self.version)
        self.dynamic_data, r, jnt = segments(self.dynamic_data, self.ofm_parameters, self.version)
        self.dynamic_data = kinematics(self.dynamic_data, r, jnt, self.version)

    def plot_angles(
        self,
        vicon_data: dict | None = None,
        plot_title: str = "",
        gsettings: dict | None = None,
    ) -> None:
        """Plot Oxford Foot Model joint angles.

        Parameters
        ----------
        vicon_data : dict or None, optional
            Vicon reference data for comparison overlay.
        plot_title : str, optional
            Figure title.
        gsettings : dict or None, optional
            Graphics settings (see: func:`~openofm.plotting.plotting.plot_angles`).
        """

        plot_angles(data=self.dynamic_data, vicon_data=vicon_data, plot_title=plot_title, gsettings=gsettings)


    def validate(self, data_dir: str) -> None:
        """Validate openOFM outputs against Vicon-processed reference data.

        Iterates over all subject folders inside ``Data_Validate/``, runs the
        static and dynamic pipelines, computes NRMSE between openOFM and the
        Vicon-generated reference, and displays comparison plots.
        """

        if self.version is not '1.0':
            print('updating version to 1.0 for validation purpuses')
            self.version = '1.0'

        # general settings for all validation trials
        settings = dict(nexus=False)        # nexus is always set to False in order to validate the python code
        settings['version'] = '1.0'        # set version of ofm model (use only 1.0 to replicate against Vicon)
        settings['use_settings'] = False   # looks for settings in .c3d file

        # get path to validation c3d files
        version = self.version

        for subject in os.listdir(data_dir):
            settings['data_dir'] = os.path.join(validation_dir, subject)  # relative to root
            print('validating openOFM using raw and processed data in folder {}'.format(settings['data_dir']))

            # get path to validation files
            fl_static_processed = os.path.join(ROOT_DIR, settings['data_dir'], static_trial_processed)
            fl_dynamic_processed = os.path.join(ROOT_DIR, settings['data_dir'], dynamic_trial_processed)

            # load c3d files to dictionary
            sdata_processed = c3d_to_dict(fl_static_processed)
            data_processed = c3d_to_dict(fl_dynamic_processed)

            # update settings to include parameters computed by OFM pipeline
            settings.update(_get_validation_settings(sdata_processed, settings))

            # run openOFM static
            settings['trial_type'] = 'static'
            settings['file_name'] = static_trial
            _, _ = openOFM_static(settings=settings)

            # run openOFM dynamic
            settings['trial_type'] = 'dynamic'
            settings['file_name'] = dynamic_trial
            settings['make_plot'] = False
            data = openOFM_dynamic(settings=settings)

            # compute normalized root mean squared error between vicon generated OFM and openOFM
            data = get_nrmse(data, data_processed)

            # compare angles between vicon generated OFM and openOFM
            plot_title = make_plot_title(settings)
            plot_angles(data=data, vicon_data=data_processed, plot_title=plot_title)


    def _get_validation_settings(sdata_processed: dict, settings: dict) -> dict:
        """Populate settings with parameter values from the Vicon OFM pipeline.

        Parameters
        ----------
        sdata_processed : dict
            Static trial data pre-processed by Vicon, containing a
            ``parameters['PROCESSING']`` block with subject measurements.
        settings : dict
            Existing settings dictionary to extend.

        Returns
        -------
        dict
            Extended settings dictionary with ``'parameters'`` and
            ``'processing'`` sub-dicts populated.
        """
        params = sdata_processed['parameters']['PROCESSING']
        settings['parameters'] = {}
        settings['parameters']['MarkerDiameter'] = int(params['MarkerDiameter']['value'][0])
        settings['parameters']['InterAsisDistance'] = int(params['InterAsisDistance']['value'][0])
        settings['parameters']['RLegLength'] = int(params['RLegLength']['value'][0])
        settings['parameters']['LLegLength'] = int(params['LLegLength']['value'][0])
        settings['parameters']['RKneeWidth'] = int(params['RKneeWidth']['value'][0])
        settings['parameters']['LKneeWidth'] = int(params['LKneeWidth']['value'][0])
        settings['parameters']['RAnkleWidth'] = int(params['RAnkleWidth']['value'][0])
        settings['parameters']['LAnkleWidth'] = int(params['LAnkleWidth']['value'][0])
        settings['parameters']['RThighRotation'] = int(params['RThighRotation']['value'][0])
        settings['parameters']['LThighRotation'] = int(params['LThighRotation']['value'][0])
        settings['parameters']['RShankRotation'] = int(params['RShankRotation']['value'][0])
        settings['parameters']['LShankRotation'] = int(params['LShankRotation']['value'][0])

        settings['processing'] = {}
        settings['processing']['RHindFootFlat'] = int(params['RHindFootFlat']['value'][0].astype(int))
        settings['processing']['LHindFootFlat'] = int(params['LHindFootFlat']['value'][0].astype(int))
        settings['processing']['RUseFloorFF'] = int(params['RUseFloorFF']['value'][0].astype(int))
        settings['processing']['LUseFloorFF'] = int(params['LUseFloorFF']['value'][0].astype(int))

        return settings