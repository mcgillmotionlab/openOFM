"""openOFM: Python implementation of the Oxford Foot Model."""

from .ofm import OFM
from .static import openOFM_static
from .dynamic import openOFM_dynamic

__all__ = ["OFM", "openOFM_static", "openOFM_dynamic"]
