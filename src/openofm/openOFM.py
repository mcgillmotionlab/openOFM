import os
from collections.abc import Callable
from typing import Union

import yaml

from .OFM.virtual_markers import create_virtual_markers, animate_virtual_markers
from .OFM.segments import segments
from .OFM.kinematics import kinematics
from .PiG.pig import hipjointcentrePiG, kneejointcenterPiG, anklejointcenterPiG
from .plotting.plotting import plot_angles
from .utils.utils import c3d_to_dict
#todo: should we split stuff about collection session (e.g. marker diameter) from subject_measurements (e.g. knee width)?




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

    def __init__(
        self,
        static_file: str | None = None,
        dynamic_file: str | None = None,
        subject_measurements: dict | None = None,
        process_options: dict | None = None,
        version: str | None = None,
    ) -> None:
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
            openOFM model version (e.g. ``'1.1'``).
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
            Graphics settings (see :func:`~openofm.plotting.plotting.plot_angles`).
        """

        plot_angles(data=self.dynamic_data, vicon_data=vicon_data, plot_title=plot_title, gsettings=gsettings)



