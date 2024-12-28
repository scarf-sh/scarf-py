"""Python bindings for Scarf telemetry."""

from .event_logger import ScarfEventLogger
from .version import __version__

__all__ = ["ScarfEventLogger", "__version__"]
