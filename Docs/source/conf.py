import os
import sys
from importlib.metadata import version as _pkg_version

sys.path.insert(0, os.path.abspath('../../src'))

project = 'openOFM'
copyright = '2026, McGill Motion Lab'
author = 'McGill Motion Lab'
try:
    release = _pkg_version('openofm')
except Exception:
    release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
]

napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_include_init_with_doc = False
napoleon_use_param = False
napoleon_use_rtype = False

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'show-inheritance': True,
    'member-order': 'bysource',
}
autodoc_typehints = 'description'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy':  ('https://numpy.org/doc/stable', None),
    'scipy':  ('https://docs.scipy.org/doc/scipy', None),
}

html_theme = 'furo'
html_static_path = ['_static']
