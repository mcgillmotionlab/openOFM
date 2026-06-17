"""openOFM: Python implementation of the Oxford Foot Model."""

from .ofm import OFM
from .openOFM_static import openOFM_static
from .openOFM_dynamic import openOFM_dynamic

__all__ = ["OFM", "openOFM_static", "openOFM_dynamic"]
