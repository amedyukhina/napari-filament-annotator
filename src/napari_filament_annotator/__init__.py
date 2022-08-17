try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._sample_data import load_sample_image
from ._widget import AnnotatorWidget

__all__ = (
    "load_sample_image",
    "AnnotatorWidget",
)
