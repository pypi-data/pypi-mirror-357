"""
ESRI Converter API

This module provides a clean, simple API for converting ESRI formats to open source formats.
All functions are designed to be called programmatically with clear return values and error handling.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging
import time

from .converters.gdb_converter import EnhancedGDBConverter
from .exceptions import ESRIConverterError, ValidationError, ConversionError


def convert_gdb_to_parquet(
    gdb_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    layers: Optional[List[str]] = None,
    chunk_size: int = 15000,
    show_progress: bool = True,
    log_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert a File Geodatabase (GDB) to GeoParquet format.
    
    Args:
        gdb_path: Path to the .gdb file or directory
        output_dir: Directory to save output files (default: "geoparquet_output")
        layers: List of specific layers to convert (default: all layers)
        chunk_size: Number of records to process at once (default: 15000)
        show_progress: Whether to show Rich progress bars (default: True)
        log_file: Optional log file path (default: None)
    
    Returns:
        Dictionary containing conversion results:
        {
            'success': bool,
            'gdb_path': str,
            'output_dir': str,
            'layers_converted': [
                {
                    'layer': str,
                    'output_file': str,
                    'record_count': int
                }
            ],
            'layers_failed': [str],
            'total_time': float,
            'total_records': int,
            'processing_rate': float,
            'output_size_mb': float
        }
    
    Raises:
        ValidationError: If input parameters are invalid
        ConversionError: If conversion fails
        ESRIConverterError: For other conversion-related errors
    
    Example:
        >>> from esri_converter.api import convert_gdb_to_parquet
        >>> result = convert_gdb_to_parquet("data.gdb")
        >>> print(f"Converted {result['total_records']} records")
    """
    # Validate inputs
    gdb_path = Path(gdb_path)
    if not gdb_path.exists():
        raise ValidationError(f"GDB path does not exist: {gdb_path}")
    
    if not gdb_path.name.endswith('.gdb'):
        raise ValidationError(f"Path is not a .gdb file: {gdb_path}")
    
    # Set up output directory
    if output_dir is None:
        output_dir = Path("geoparquet_output")
    else:
        output_dir = Path(output_dir)
    
    # Configure logging if needed
    if log_file:
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    try:
        # Initialize converter
        converter = EnhancedGDBConverter(str(output_dir))
        
        # Perform conversion
        result = converter.convert_gdb_enhanced(
            str(gdb_path),
            layers=layers,
            chunk_size=chunk_size
        )
        
        # Check for errors
        if 'error' in result:
            raise ConversionError(f"Conversion failed: {result['error']}")
        
        # Calculate additional metrics
        total_records = sum(
            layer['record_count'] for layer in result.get('layers_converted', [])
        )
        
        processing_rate = 0
        if result.get('total_time', 0) > 0:
            processing_rate = total_records / result['total_time']
        
        # Calculate output size
        output_size_mb = 0
        output_path = Path(result.get('output_dir', output_dir))
        if output_path.exists():
            for parquet_file in output_path.rglob("*.parquet"):
                output_size_mb += parquet_file.stat().st_size / (1024 * 1024)
        
        # Return enhanced result
        return {
            'success': len(result.get('layers_failed', [])) == 0,
            'gdb_path': str(gdb_path),
            'output_dir': result.get('output_dir', str(output_dir)),
            'layers_converted': result.get('layers_converted', []),
            'layers_failed': result.get('layers_failed', []),
            'total_time': result.get('total_time', 0),
            'total_records': total_records,
            'processing_rate': processing_rate,
            'output_size_mb': output_size_mb
        }
        
    except Exception as e:
        if isinstance(e, ESRIConverterError):
            raise
        else:
            raise ConversionError(f"Unexpected error during conversion: {str(e)}")


def convert_multiple_gdbs(
    gdb_paths: List[Union[str, Path]],
    output_dir: Optional[Union[str, Path]] = None,
    chunk_size: int = 15000,
    show_progress: bool = True,
    log_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert multiple GDB files to GeoParquet format.
    
    Args:
        gdb_paths: List of paths to .gdb files
        output_dir: Directory to save output files (default: "geoparquet_output")
        chunk_size: Number of records to process at once (default: 15000)
        show_progress: Whether to show Rich progress bars (default: True)
        log_file: Optional log file path (default: None)
    
    Returns:
        Dictionary containing conversion results for all GDBs:
        {
            'success': bool,
            'total_gdbs': int,
            'gdbs_converted': int,
            'gdbs_failed': int,
            'results': [
                # Individual GDB results (same format as convert_gdb_to_parquet)
            ],
            'total_time': float,
            'total_records': int,
            'total_output_size_mb': float
        }
    
    Example:
        >>> from esri_converter.api import convert_multiple_gdbs
        >>> result = convert_multiple_gdbs(["data1.gdb", "data2.gdb"])
        >>> print(f"Converted {result['gdbs_converted']}/{result['total_gdbs']} GDBs")
    """
    if not gdb_paths:
        raise ValidationError("No GDB paths provided")
    
    results = []
    total_start_time = time.time()
    
    for gdb_path in gdb_paths:
        try:
            result = convert_gdb_to_parquet(
                gdb_path=gdb_path,
                output_dir=output_dir,
                chunk_size=chunk_size,
                show_progress=show_progress,
                log_file=log_file
            )
            results.append(result)
        except Exception as e:
            # Add failed result
            results.append({
                'success': False,
                'gdb_path': str(gdb_path),
                'error': str(e),
                'layers_converted': [],
                'layers_failed': [],
                'total_time': 0,
                'total_records': 0,
                'processing_rate': 0,
                'output_size_mb': 0
            })
    
    total_time = time.time() - total_start_time
    
    # Calculate summary statistics
    gdbs_converted = sum(1 for r in results if r['success'])
    gdbs_failed = len(results) - gdbs_converted
    total_records = sum(r['total_records'] for r in results)
    total_output_size_mb = sum(r['output_size_mb'] for r in results)
    
    return {
        'success': gdbs_failed == 0,
        'total_gdbs': len(gdb_paths),
        'gdbs_converted': gdbs_converted,
        'gdbs_failed': gdbs_failed,
        'results': results,
        'total_time': total_time,
        'total_records': total_records,
        'total_output_size_mb': total_output_size_mb
    }


def discover_gdb_files(directory: Union[str, Path] = ".") -> List[Path]:
    """
    Discover all .gdb files in a directory.
    
    Args:
        directory: Directory to search for .gdb files (default: current directory)
    
    Returns:
        List of Path objects pointing to .gdb files
    
    Example:
        >>> from esri_converter.api import discover_gdb_files
        >>> gdb_files = discover_gdb_files("data/")
        >>> print(f"Found {len(gdb_files)} GDB files")
    """
    directory = Path(directory)
    if not directory.exists():
        raise ValidationError(f"Directory does not exist: {directory}")
    
    if not directory.is_dir():
        raise ValidationError(f"Path is not a directory: {directory}")
    
    gdb_files = [f for f in directory.iterdir() if f.is_dir() and f.name.endswith('.gdb')]
    return sorted(gdb_files)


def get_gdb_info(gdb_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about a GDB file without converting it.
    
    Args:
        gdb_path: Path to the .gdb file
    
    Returns:
        Dictionary containing GDB information:
        {
            'gdb_path': str,
            'layers': [
                {
                    'name': str,
                    'record_count': int,
                    'geometry_type': str,
                    'crs': str,
                    'field_count': int,
                    'bounds': [minx, miny, maxx, maxy]
                }
            ],
            'total_records': int,
            'total_layers': int
        }
    
    Example:
        >>> from esri_converter.api import get_gdb_info
        >>> info = get_gdb_info("data.gdb")
        >>> print(f"GDB has {info['total_layers']} layers with {info['total_records']} total records")
    """
    import fiona
    
    gdb_path = Path(gdb_path)
    if not gdb_path.exists():
        raise ValidationError(f"GDB path does not exist: {gdb_path}")
    
    try:
        layers = fiona.listlayers(str(gdb_path))
    except Exception as e:
        raise ConversionError(f"Cannot read GDB layers: {e}")
    
    layer_info = []
    total_records = 0
    
    for layer_name in layers:
        try:
            with fiona.open(str(gdb_path), layer=layer_name) as src:
                record_count = len(src)
                schema = src.schema
                crs = src.crs
                bounds = src.bounds
                
                layer_info.append({
                    'name': layer_name,
                    'record_count': record_count,
                    'geometry_type': schema.get('geometry', 'Unknown'),
                    'crs': str(crs) if crs else 'Unknown',
                    'field_count': len(schema.get('properties', {})),
                    'bounds': list(bounds) if bounds else None
                })
                
                total_records += record_count
                
        except Exception as e:
            # Add layer with error info
            layer_info.append({
                'name': layer_name,
                'record_count': 0,
                'geometry_type': 'Error',
                'crs': 'Unknown',
                'field_count': 0,
                'bounds': None,
                'error': str(e)
            })
    
    return {
        'gdb_path': str(gdb_path),
        'layers': layer_info,
        'total_records': total_records,
        'total_layers': len(layers)
    }


# Import time for the multiple GDBs function
import time 