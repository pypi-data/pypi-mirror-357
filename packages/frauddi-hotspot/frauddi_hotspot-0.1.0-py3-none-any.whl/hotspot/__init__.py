"""Hotspot - Find data concentration patterns and hotspots.

Created by Elio Rincón at Frauddi.
"""

__version__ = "0.1.0"
__author__ = "Elio Rincón"
__email__ = "team@frauddi.com"
__maintainer__ = "Frauddi Team"
__license__ = "MIT"
__url__ = "https://github.com/frauddi/hotspot"

# Public API exports
from hotspot.core import Hotspot
from hotspot.exceptions import (
    ConfigurationError,
    DataError,
    HotspotError,
    QueryError,
    ValidationError,
)

# from .query import QueryBuilder  # Will add when we create it
# from .utils import quick_analysis, find_concentrations, top_patterns  # Will add when we create it


# Quick functions for easy usage
def find(data, fields, **kwargs):
    """Quick function to find concentration patterns."""
    hotspot = Hotspot()
    return hotspot.find(data, fields, **kwargs)


def analyze(data, fields, **kwargs):
    """Quick function to analyze data and get insights."""
    hotspot = Hotspot()
    return hotspot.analyze(data, fields, **kwargs)


# Package metadata
__all__ = [
    # Main classes
    "Hotspot",
    # Quick functions
    "find",
    "analyze",
    # Exceptions
    "HotspotError",
    "ValidationError",
    "DataError",
    "QueryError",
    "ConfigurationError",
]
