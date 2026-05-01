import os
from python.OFM.virtual_markers import create_virtual_markers
from utils.utils import c3d_to_dict, find_repo_root, get_python_settings,  make_plot_title

#todo: should we split stufff about collection session (e.g. marker diameter) from subject_measurements (e.g. knee width)?

class openOFM:

    def __init__(self, static_file=None, dynamic_file=None, subject_measurements=None, process_options=None,
                 version=1.1):
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

               version : float or str
                   OpenOFM pipeline version. Controls model definitions and
                   algorithmic variations across releases.

               Notes
               -----
               Processing follows a two-stage workflow:
               1. Static calibration defines subject-specific model parameters
               2. Dynamic trials are processed using static-derived calibration

               Static processing must be completed before dynamic processing.
               """

        # file inputs
        self.static_file = static_file
        self.dynamic_file = dynamic_file

        # subject anthropometric parameters
        self.subject_params = subject_measurements

        # configuration
        self.processing_options = process_options
        self.version=version

        # bookkeeping
        self.is_static_processed = False
        self.is_dynamic_processed = False

        # 👇 declare ALL expected attributes here
        self.static_data = None
        self.dynamic_data = None


    def load_static_data(self):
        """ loads static data from c3d file to a dictionary"""

        if self.static_file is None:
            raise ValueError("static file must be set first")

        if not os.path.exists(self.static_file):
            raise FileNotFoundError('File {} not found'.format(self.static_file))

        self.static_data = c3d_to_dict(self.static_file)


    def load_dynamic_data(self):
        """ loads dynamic data from c3d file to a dictionary"""

        if self.dynamic_file is None:
            raise ValueError("Dynamic file must be set first")

        if not os.path.exists(self.static_file):
            raise FileNotFoundError('File {} not found'.format(self.static_file))

        self.dynamic_data = c3d_to_dict(self.dynamic_file)


    def create_static_virtual_markers(self):

        if self.static_data is None:
            raise ValueError('Static data not loaded. Call load_static_data() first.')

        if self.processing_options is None:
            raise ValueError('Processing options must be defined before running virtual marker computation.')

        self.static_data = create_virtual_markers(self.static_data, self.processing_options, self.version)
