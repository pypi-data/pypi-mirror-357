# pyqdpx/__init__.py

from .pyqdpx import QDPX, User, Code, Source

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for when the package is not installed or setuptools_scm hasn't run yet
    __version__ = "unknown"

__author__ = "Pethő Gergely"
__email__ = "petho.gergely@etk.unideb.hu"