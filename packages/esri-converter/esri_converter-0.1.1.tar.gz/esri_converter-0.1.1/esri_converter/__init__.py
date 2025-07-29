"""
ESRI Converter - Modern tools for converting ESRI proprietary formats to open source formats.

This package provides efficient, modern tools for converting ESRI file formats
(like File Geodatabases) to open source geospatial formats (like GeoParquet).

Key Features:
- Large-scale data processing with streaming support
- Beautiful progress tracking with Rich
- Modern Python stack (Polars, DuckDB, PyArrow)
- Memory-efficient chunk-based processing
- Robust error handling and type safety

Example:
    >>> from esri_converter import convert_gdb_to_parquet
    >>> result = convert_gdb_to_parquet("data.gdb")
    >>> print(f"Converted {result['total_records']} records")
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("esri-converter")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "unknown"

# Core API functions
from .api import convert_gdb_to_parquet, convert_multiple_gdbs, discover_gdb_files, get_gdb_info

# Core converter classes
from .converters.geoparquet_converter import GeoParquetConverter
from .converters.geoparquet_converter import (
    GeoParquetConverter as GDBConverter,  # Alias for backward compatibility
)

# Core exceptions
from .exceptions import (
    ConversionError,
    ESRIConverterError,
    UnsupportedFormatError,
    ValidationError,
)

# Utility functions
from .utils.formats import get_format_info, list_supported_formats
from .utils.validation import validate_gdb_file, validate_output_path

__all__ = [
    "__version__",
    # Core API functions
    "convert_gdb_to_parquet",
    "convert_multiple_gdbs",
    "discover_gdb_files",
    "get_gdb_info",
    # Converters
    "GDBConverter",
    "GeoParquetConverter",
    # Utilities
    "list_supported_formats",
    "get_format_info",
    "validate_gdb_file",
    "validate_output_path",
    # Exceptions
    "ESRIConverterError",
    "UnsupportedFormatError",
    "ValidationError",
    "ConversionError",
]

# Package metadata
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"
__description__ = "Modern tools for converting ESRI proprietary formats to open source formats"
