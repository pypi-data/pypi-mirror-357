from importlib.metadata import PackageNotFoundError, version

from .api import _code_generator, _constructor, preset_table
from .api import *
from .util import *
from .knowledge_graph_construction import find_closest_metadata

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "im2im"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
