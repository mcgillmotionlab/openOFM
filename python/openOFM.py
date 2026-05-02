import os
import yaml
from typing import Callable, Union

from python.OFM.virtual_markers import create_virtual_markers
from utils.utils import c3d_to_dict
from python.PiG.pig import hipjointcentrePiG, kneejointcenterPiG, anklejointcenterPiG
#todo: should we split stufff about collection session (e.g. marker diameter) from subject_measurements (e.g. knee width)?




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

    def __init__(self, static_file=None, dynamic_file=None, subject_measurements=None, process_options=None,
                 version=None):
        """
               OpenOFM main class for processing static and dynamic gait trials.

               Parameters
               ----------
               static_file : str or None
                   Path to the static calibration C3D file. Used to define subject-specific anatomical calibration
                   (e.g., virtual markers, joint geometry). If None, static data must be loaded manually.

               dynamic_file : str or None
                   Path to the dynamic gait trial C3D file. If None, dynamic data must be loaded manually before
                   processing.

               subject_measurements : dict or None
                   Subject-specific Anthropometric parameters (e.g., ankle width, knee width) and settings
                   (e.g. marker diameter). Used in model scaling and biomechanical computations.

               process_options : dict or None
                   Configuration dictionary controlling processing behaviour
                   (e.g., filtering settings, gait event detection method,
                   joint center computation methods).

               version : float or None
                   OpenOFM pipeline version. Controls model definitions and algorithmic variations across releases.

               Notes
               -----
               Processing follows a two-stage workflow:
               1. Static calibration defines subject-specific model parameters
               2. Dynamic trials are processed using static-derived calibration

               Static processing must be completed before dynamic processing.
               """

        # version must be set
        if version is None:
            raise ValueError("version must be specified at initialization")

        # file inputs
        self.static_file = static_file
        self.dynamic_file = dynamic_file

        # subject anthropometric parameters
        self.subject_measurements = subject_measurements

        # configuration
        self.processing_options = process_options
        self.version=version

        # bookkeeping
        self.is_static_processed = False
        self.is_dynamic_processed = False

        # 👇 declare ALL expected attributes here
        self.static_data = None
        self.dynamic_data = None


    def load_static_file(self, filepath=None):
        """Loads static file data from c3d file to a dictionary"""

        if filepath is not None:
            self.static_file = filepath

        if self.static_file is None:
            raise ValueError("static file must be set before loading if not using an argument")

        if not os.path.exists(self.static_file):
            raise FileNotFoundError('Static file {} not found'.format(self.static_file))

        self.static_data = c3d_to_dict(self.static_file)


    def load_dynamic_file(self, filepath=None):
        """ loads dynamic file data from c3d file to a dictionary"""

        if filepath is not None:
            self.static_file = filepath

        if self.dynamic_file is None:
            raise ValueError("dynamic file must be set before loading if not using an argument")

        if not os.path.exists(self.dynamic_file):
            raise FileNotFoundError('Dynamic file {} not found'.format(self.dynamic_file))

        self.dynamic_data = c3d_to_dict(self.dynamic_file)

    def load_subject_measurements(self, filepath):
        """Load subject measurements from a YAML file stored in filepath."""

        if not os.path.exists(filepath):
            raise FileNotFoundError('File {} not found'.format(filepath))

        with open(filepath, 'r') as f:
            self.subject_params = yaml.safe_load(f)

    def process_static_trial(self, subject_measurements=None, process_options=None):

        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        if subject_measurements is None:
            raise ValueError('Subject measurements not loaded. Either specify path to subject measurements or Call '
                             'load_subject_measurements() first.')

        if self.processing_options is None:
            self.processing_options = self.DEFAULT_PROCESSING_OPTIONS.copy()

        self.static_data = create_virtual_markers(self.static_data, self.processing_options, self.version)

    def compute_hip_joint_center(self, method: HJCMethod = 'pig'):

        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        # --- built-in method ---
        if method == 'pig':
            self.static_data = hipjointcentrePiG(self.static_data)

        # --- user-defined function ---
        elif callable(method):
            self.static_data = method(self.static_data)

        else:
            raise ValueError("Unknown method '{}'. Use 'pig' or provide a callable function.".format(method))


    def compute_knee_joint_center(self, method: KJCMethod = 'pig'):

        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        # --- built-in method ---
        if method == 'pig':
            self.static_data = kneejointcenterPiG(self.static_data)

        # --- user-defined function ---
        elif callable(method):
            self.static_data = method(self.static_data)

        else:
            raise ValueError("Unknown method '{}'. Use 'pig' or provide a callable function.".format(method))

    def compute_ankle_joint_center(self, method: AJCMethod = 'pig'):

        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_file() first.')

        # --- built-in method ---
        if method == 'pig':
            self.static_data = anklejointcenterPiG(self.static_data)

        # --- user-defined function ---
        elif callable(method):
            self.static_data = method(self.static_data)

        else:
            raise ValueError("Unknown method '{}'. Use 'pig' or provide a callable function.".format(method)
            )