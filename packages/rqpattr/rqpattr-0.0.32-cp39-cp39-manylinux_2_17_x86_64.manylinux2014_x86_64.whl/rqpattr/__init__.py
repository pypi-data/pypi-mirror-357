from .api import performance_attribute, returns_decomposition

__all__ = ["performance_attribute", "returns_decomposition"]

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions
