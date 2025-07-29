# Changelog

All notable changes to the ESRI Converter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-06-22

### Added
- **OGC GeoParquet Compliance**: Now produces valid GeoParquet files according to the OGC GeoParquet v1.0.0 specification
- New `GeoParquetConverter` class replacing the old non-compliant converter
- GeoPandas dependency for proper GeoParquet generation
- Verification scripts for testing GeoParquet compliance

### Changed
- Complete rewrite of the converter to produce OGC-compliant GeoParquet files
- Geometry storage changed from WKT text to WKB binary format
- CRS information is now properly preserved in geo metadata
- Updated documentation to reflect GeoParquet compliance

### Removed
- Legacy `EnhancedGDBConverter` that produced non-standard parquet files
- `use_legacy_converter` parameter (all output is now GeoParquet compliant)

### Fixed
- Output files can now be read by standard GeoParquet readers (GeoPandas, DuckDB Spatial, QGIS, etc.)
- Added required geo metadata to parquet file headers
- Geometry data now stored in standard `geometry` column
- Fixed interoperability with the broader geospatial ecosystem

## [0.1.0] - 2025-01-28

### Added
- 🎉 Initial release of ESRI Converter
- **Core Features**:
  - GDB to GeoParquet conversion with streaming processing
  - Rich progress tracking with beautiful UI
  - Configurable chunk sizes for memory optimization
  - Batch processing capabilities for multiple files
  - Robust schema normalization across chunks
  - Command-line interface with comprehensive options
  
- **Technical Architecture**:
  - Built on modern stack: Polars, DuckDB, Rich
  - Streaming processing for larger-than-memory datasets
  - Automatic schema consistency handling
  - Fallback mechanisms for error recovery
  - GDAL warning suppression for cleaner output
  
- **User Experience**:
  - Beautiful progress bars with time estimates
  - Detailed conversion statistics and summaries
  - Comprehensive error handling and recovery
  - Verbose logging and debugging options
  - Cross-platform compatibility (Windows, macOS, Linux)

- **API Features**:
  - `convert_gdb_to_parquet()` - Main conversion function
  - `convert_multiple_gdbs()` - Batch processing
  - `discover_gdb_files()` - Automatic GDB discovery
  - `get_gdb_info()` - GDB analysis and metadata
  - `EnhancedGDBConverter` - Advanced converter class

- **Command Line Tools**:
  - `esri-convert` - Main CLI entry point
  - `gdb2parquet` - Direct conversion command
  - Comprehensive argument support for all options

- **Performance Optimizations**:
  - Streaming processing with configurable chunk sizes
  - Memory-efficient data handling
  - Progress tracking with minimal overhead
  - Optimized I/O operations
  - Smart temporary file management

- **Documentation**:
  - Comprehensive MkDocs documentation website
  - API reference with examples
  - Performance optimization guides
  - Development and contribution guidelines
  - Automatic deployment to GitHub Pages

### Dependencies

- **Core**: polars (≥0.20.0), fiona (≥1.9.0), pyarrow (≥15.0.0)
- **Geospatial**: shapely (≥2.0.0)
- **UI**: rich (≥13.0.0), tqdm (≥4.65.0)
- **Utilities**: psutil (≥5.9.0)
- **Documentation**: mkdocs and related plugins

### Performance Benchmarks

Initial benchmarks on test datasets:

| Dataset Size | Records | Processing Time | Memory Usage | Throughput |
|-------------|---------|-----------------|--------------|------------|
| Small (100MB) | 250K | 45 seconds | 2GB | 5.6K records/sec |
| Medium (1GB) | 1.2M | 3.2 minutes | 4GB | 6.3K records/sec |
| Large (5GB) | 5.9M | 12.8 minutes | 6GB | 7.7K records/sec |

### Known Issues

- Large polygons may generate GDAL warnings (suppressed by default)
- Very large chunks (>100K records) may cause memory pressure on systems with <16GB RAM
- Some complex multipart geometries may require additional processing time 