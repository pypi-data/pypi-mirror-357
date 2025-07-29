"""
Validation utilities for ESRI Converter.

This module provides functions to validate input files, paths, and parameters.
"""

from pathlib import Path
from typing import Union, List, Optional
import fiona

from ..exceptions import ValidationError


def validate_gdb_file(gdb_path: Union[str, Path]) -> bool:
    """
    Validate that a path points to a valid GDB file.
    
    Args:
        gdb_path: Path to the .gdb file
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If the GDB file is invalid
    
    Example:
        >>> from esri_converter.utils import validate_gdb_file
        >>> validate_gdb_file("data.gdb")  # Returns True or raises ValidationError
    """
    gdb_path = Path(gdb_path)
    
    # Check if path exists
    if not gdb_path.exists():
        raise ValidationError(f"GDB path does not exist: {gdb_path}")
    
    # Check if it's a directory
    if not gdb_path.is_dir():
        raise ValidationError(f"GDB path is not a directory: {gdb_path}")
    
    # Check if it has .gdb extension
    if not gdb_path.name.endswith('.gdb'):
        raise ValidationError(f"Path does not have .gdb extension: {gdb_path}")
    
    # Try to open with fiona to verify it's a valid GDB
    try:
        layers = fiona.listlayers(str(gdb_path))
        if not layers:
            raise ValidationError(f"GDB contains no layers: {gdb_path}")
    except Exception as e:
        raise ValidationError(f"Cannot read GDB file: {gdb_path}. Error: {str(e)}")
    
    return True


def validate_output_path(output_path: Union[str, Path], create_if_missing: bool = True) -> bool:
    """
    Validate that an output path is writable.
    
    Args:
        output_path: Path for output files
        create_if_missing: Whether to create the directory if it doesn't exist
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If the output path is invalid
    
    Example:
        >>> from esri_converter.utils import validate_output_path
        >>> validate_output_path("output/")  # Returns True or raises ValidationError
    """
    output_path = Path(output_path)
    
    # If it's a file path, get the parent directory
    if output_path.suffix:
        parent_dir = output_path.parent
    else:
        parent_dir = output_path
    
    # Check if parent directory exists
    if not parent_dir.exists():
        if create_if_missing:
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(f"Cannot create output directory: {parent_dir}. Error: {str(e)}")
        else:
            raise ValidationError(f"Output directory does not exist: {parent_dir}")
    
    # Check if directory is writable
    if not parent_dir.is_dir():
        raise ValidationError(f"Output path is not a directory: {parent_dir}")
    
    # Test write permissions by creating a temporary file
    test_file = parent_dir / ".test_write_permissions"
    try:
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        raise ValidationError(f"Output directory is not writable: {parent_dir}. Error: {str(e)}")
    
    return True


def validate_layers(gdb_path: Union[str, Path], layers: List[str]) -> List[str]:
    """
    Validate that specified layers exist in the GDB.
    
    Args:
        gdb_path: Path to the .gdb file
        layers: List of layer names to validate
    
    Returns:
        List of valid layer names
    
    Raises:
        ValidationError: If layers are invalid
    
    Example:
        >>> from esri_converter.utils import validate_layers
        >>> valid_layers = validate_layers("data.gdb", ["layer1", "layer2"])
    """
    gdb_path = Path(gdb_path)
    
    # First validate the GDB itself
    validate_gdb_file(gdb_path)
    
    # Get available layers
    try:
        available_layers = fiona.listlayers(str(gdb_path))
    except Exception as e:
        raise ValidationError(f"Cannot list layers in GDB: {gdb_path}. Error: {str(e)}")
    
    # Check each requested layer
    invalid_layers = []
    valid_layers = []
    
    for layer in layers:
        if layer in available_layers:
            valid_layers.append(layer)
        else:
            invalid_layers.append(layer)
    
    if invalid_layers:
        raise ValidationError(
            f"Invalid layers: {invalid_layers}. Available layers: {available_layers}"
        )
    
    return valid_layers


def validate_chunk_size(chunk_size: int, record_count: Optional[int] = None) -> int:
    """
    Validate and potentially adjust chunk size.
    
    Args:
        chunk_size: Requested chunk size
        record_count: Total number of records (optional)
    
    Returns:
        Validated chunk size
    
    Raises:
        ValidationError: If chunk size is invalid
    
    Example:
        >>> from esri_converter.utils import validate_chunk_size
        >>> chunk_size = validate_chunk_size(10000, 50000)
    """
    if not isinstance(chunk_size, int):
        raise ValidationError(f"Chunk size must be an integer, got: {type(chunk_size)}")
    
    if chunk_size <= 0:
        raise ValidationError(f"Chunk size must be positive, got: {chunk_size}")
    
    # Reasonable limits
    if chunk_size > 100000:
        raise ValidationError(f"Chunk size too large (max 100,000), got: {chunk_size}")
    
    if chunk_size < 100:
        raise ValidationError(f"Chunk size too small (min 100), got: {chunk_size}")
    
    # If we know the record count, adjust if necessary
    if record_count is not None:
        if chunk_size > record_count:
            # Chunk size larger than total records - use total records
            return record_count
    
    return chunk_size


def validate_format(format_name: str) -> str:
    """
    Validate output format name.
    
    Args:
        format_name: Name of the output format
    
    Returns:
        Normalized format name
    
    Raises:
        ValidationError: If format is not supported
    
    Example:
        >>> from esri_converter.utils import validate_format
        >>> format_name = validate_format("parquet")  # Returns "parquet"
    """
    from .formats import list_supported_formats
    
    supported_formats = list_supported_formats()
    output_formats = supported_formats['output']
    
    format_lower = format_name.lower().strip()
    
    if format_lower not in output_formats:
        raise ValidationError(
            f"Unsupported output format: {format_name}. "
            f"Supported formats: {', '.join(output_formats)}"
        )
    
    return format_lower


def validate_api_parameters(
    gdb_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    layers: Optional[List[str]] = None,
    chunk_size: int = 15000,
    output_format: str = "parquet"
) -> dict:
    """
    Validate all API parameters at once.
    
    Args:
        gdb_path: Path to the .gdb file
        output_dir: Output directory path
        layers: List of layer names
        chunk_size: Chunk size for processing
        output_format: Output format name
    
    Returns:
        Dictionary of validated parameters
    
    Raises:
        ValidationError: If any parameter is invalid
    
    Example:
        >>> from esri_converter.utils import validate_api_parameters
        >>> params = validate_api_parameters("data.gdb", chunk_size=5000)
    """
    validated = {}
    
    # Validate GDB path
    validate_gdb_file(gdb_path)
    validated['gdb_path'] = Path(gdb_path)
    
    # Validate output directory
    if output_dir is None:
        output_dir = Path("geoparquet_output")
    else:
        output_dir = Path(output_dir)
    
    validate_output_path(output_dir, create_if_missing=True)
    validated['output_dir'] = output_dir
    
    # Validate layers if specified
    if layers is not None:
        validated['layers'] = validate_layers(gdb_path, layers)
    else:
        validated['layers'] = None
    
    # Validate chunk size
    validated['chunk_size'] = validate_chunk_size(chunk_size)
    
    # Validate output format
    validated['output_format'] = validate_format(output_format)
    
    return validated 