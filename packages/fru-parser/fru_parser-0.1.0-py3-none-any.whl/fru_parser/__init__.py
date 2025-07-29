from importlib import metadata

from .parser import parse_fru

try:
    __version__ = metadata.version("fru-parser")
except metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["parse_fru", "__version__"]