"""openOFM: Python implementation of the Oxford Foot Model."""

from .openofm import openOFM
from .static import openOFM_static
from .dynamic import openOFM_dynamic

__all__ = ["openOFM", "openOFM_static", "openOFM_dynamic"]
