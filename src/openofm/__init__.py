"""openOFM: Python implementation of the Oxford Foot Model."""

from .openOFM import openOFM
from .static import openOFM_static
from .dynamic import openOFM_dynamic

__version__ = "0.1.0"
__all__ = ["openOFM", "openOFM_static", "openOFM_dynamic"]
