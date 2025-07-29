"""
Format support utilities for ESRI Converter.

This module provides information about supported input and output formats.
"""

from typing import Any


def list_supported_formats() -> dict[str, list[str]]:
    """
    List all supported input and output formats.

    Returns:
        Dictionary with 'input' and 'output' keys containing lists of supported formats

    Example:
        >>> from esri_converter.utils import list_supported_formats
        >>> formats = list_supported_formats()
        >>> print(f"Input formats: {formats['input']}")
        >>> print(f"Output formats: {formats['output']}")
    """
    return {
        "input": [
            "gdb",  # ESRI File Geodatabase
            # Future: 'shp', 'mdb', 'lyr', etc.
        ],
        "output": [
            "parquet",  # GeoParquet
            "geoparquet",  # GeoParquet (alias)
            # Future: 'geojson', 'gpkg', 'csv', etc.
        ],
    }


def get_format_info(format_name: str) -> dict[str, Any]:
    """
    Get detailed information about a specific format.

    Args:
        format_name: Name of the format (e.g., 'gdb', 'parquet')

    Returns:
        Dictionary containing format information

    Example:
        >>> from esri_converter.utils import get_format_info
        >>> info = get_format_info('gdb')
        >>> print(f"Description: {info['description']}")
    """
    formats = {
        "gdb": {
            "name": "ESRI File Geodatabase",
            "description": "ESRI proprietary geodatabase format for storing geospatial data",
            "extensions": [".gdb"],
            "type": "input",
            "supports_multiple_layers": True,
            "supports_geometry": True,
            "supports_attributes": True,
            "typical_size": "Large (GB+)",
            "compression": "Proprietary",
        },
        "parquet": {
            "name": "GeoParquet",
            "description": "Open source columnar storage format optimized for geospatial data",
            "extensions": [".parquet"],
            "type": "output",
            "supports_multiple_layers": False,  # One file per layer
            "supports_geometry": True,  # As WKT
            "supports_attributes": True,
            "typical_size": "Compressed (10-50% of original)",
            "compression": "Snappy, GZIP, LZ4, etc.",
        },
        "geoparquet": {
            "name": "GeoParquet",
            "description": "Alias for parquet format with geospatial extensions",
            "extensions": [".parquet"],
            "type": "output",
            "supports_multiple_layers": False,
            "supports_geometry": True,
            "supports_attributes": True,
            "typical_size": "Compressed (10-50% of original)",
            "compression": "Snappy, GZIP, LZ4, etc.",
        },
    }

    format_lower = format_name.lower()
    if format_lower not in formats:
        return {
            "name": format_name,
            "description": "Unknown format",
            "error": f'Format "{format_name}" is not supported',
        }

    return formats[format_lower]


def get_recommended_chunk_size(record_count: int, geometry_complexity: str = "medium") -> int:
    """
    Get recommended chunk size based on record count and geometry complexity.

    Args:
        record_count: Total number of records to process
        geometry_complexity: 'simple', 'medium', or 'complex'

    Returns:
        Recommended chunk size

    Example:
        >>> from esri_converter.utils import get_recommended_chunk_size
        >>> chunk_size = get_recommended_chunk_size(1000000, 'complex')
        >>> print(f"Recommended chunk size: {chunk_size}")
    """
    # Base chunk sizes by complexity
    base_sizes = {
        "simple": 25000,  # Points, simple polygons
        "medium": 15000,  # Standard polygons
        "complex": 8000,  # Complex polygons, multipolygons
    }

    base_size = base_sizes.get(geometry_complexity.lower(), 15000)

    # Adjust based on total record count
    if record_count < 10000:
        # Small datasets - process all at once
        return record_count
    elif record_count < 100000:
        # Medium datasets - use smaller chunks
        return min(base_size // 2, record_count)
    else:
        # Large datasets - use recommended chunk size
        return base_size


def estimate_output_size(
    record_count: int, field_count: int, geometry_type: str = "Polygon"
) -> dict[str, float]:
    """
    Estimate output file size for different formats.

    Args:
        record_count: Number of records
        field_count: Number of attribute fields
        geometry_type: Type of geometry ('Point', 'Polygon', etc.)

    Returns:
        Dictionary with estimated sizes in MB for different formats

    Example:
        >>> from esri_converter.utils import estimate_output_size
        >>> sizes = estimate_output_size(100000, 50, 'Polygon')
        >>> print(f"Estimated GeoParquet size: {sizes['parquet']:.1f} MB")
    """
    # Rough estimates based on typical data
    bytes_per_record = {
        "Point": 200,  # Small geometries
        "LineString": 500,  # Medium geometries
        "Polygon": 800,  # Larger geometries
        "MultiPolygon": 1200,  # Complex geometries
    }

    base_bytes = bytes_per_record.get(geometry_type, 800)

    # Add bytes for attributes (rough estimate)
    attribute_bytes = field_count * 20  # Average 20 bytes per field

    total_bytes_per_record = base_bytes + attribute_bytes
    total_bytes = record_count * total_bytes_per_record

    # Compression ratios for different formats
    compression_ratios = {
        "parquet": 0.3,  # 30% of original (Snappy compression)
        "geoparquet": 0.3,  # Same as parquet
        "geojson": 1.2,  # 120% (text format, larger than binary)
        "csv": 0.8,  # 80% (no geometry, just attributes)
    }

    estimates = {}
    for format_name, ratio in compression_ratios.items():
        size_mb = (total_bytes * ratio) / (1024 * 1024)
        estimates[format_name] = round(size_mb, 2)

    return estimates
