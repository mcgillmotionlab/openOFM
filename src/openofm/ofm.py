import os
from collections.abc import Callable
from typing import Union

import yaml

from openofm.core.virtual_markers import create_virtual_markers, animate_virtual_markers
from openofm.core.segments import segments
from openofm.core.kinematics import kinematics
from openofm.core.pig import hipjointcentrePiG, kneejointcenterPiG, anklejointcenterPiG
from openofm.plotting.plotting import plot_angles
from openofm.utils.utils import c3d_to_dict


#todo: should we split stuff about collection session (e.g. marker diameter) from subject_measurements (e.g. knee width)?
#todo: initialize with version 1.0 instead of None and raising an error?



class OFM:


    DEFAULT_PROCESSING_OPTIONS = {
        'RUseFloorFF': False,
        'LUseFloorFF': False,
        'RHindFootFlat': True,
        'LHindFootFlat': True,
    }

    HJCMethod = Union[str, Callable[[dict], dict]]
    KJCMethod = Union[str, Callable[[dict], dict]]
    AJCMethod = Union[str, Callable[[dict], dict]]

    def __init__(self, version: str | None = None) -> None:
        """Initialise an openOFM processing session.

        Parameters
        ----------
        version : str or None, optional
            openOFM model version. Options 1.0 or 1.1.
        """

        # version must be set
        if version is None:
            raise ValueError("version must be specified at initialization")

        # configuration
        self.version=version

        # bookkeeping
        self.is_static_processed = False
        self.is_dynamic_processed = False

        self.static_data = None
        self.dynamic_data = None
        self.ofm_parameters = None
        self.subject_parameters = None
        self.process_options = None

        print('initialized ofm object using version = {}'.format(self.version))

    def load_static_data(self, filepath: str) -> None:
        """Load static trial data from a C3D file.

        Parameters
        ----------
        filepath : str
            Path to the static C3D file.
        """

        if not os.path.exists(filepath):
            raise FileNotFoundError('Static file {} not found'.format(filepath))

        self.static_data = c3d_to_dict(filepath)


    def load_dynamic_data(self, filepath: str) -> None:
        """Load dynamic trial data from a C3D file.

        Parameters
        ----------
        filepath : str o
            Path to the dynamic C3D file.
        """

        if not os.path.exists(filepath):
            raise FileNotFoundError('Dynamic file {} not found'.format(filepath))

        self.dynamic_data = c3d_to_dict(filepath)

    def load_subject_parameters(self, filepath: str) -> None:
        """Load subject related parameters from a YAML file.

        Parameters
        ----------
        filepath : str
            Path to ``subject_measurements.yml``.
        """

        if not os.path.exists(filepath):
            raise FileNotFoundError('File {} not found'.format(filepath))

        with open(filepath, 'r') as f:
            self.subject_parameters = yaml.safe_load(f)


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

        if self.subject_parameters is None:
            raise ValueError('Subject measurements not loaded. Call load_subject_parameters() first.')

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

    def process_dynamic_trial(self) -> None:
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