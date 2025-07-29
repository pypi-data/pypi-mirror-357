#!/usr/bin/env python3
"""
Enhanced Large-Scale GDB to GeoParquet Converter
Uses Rich for beautiful logging, progress tracking, and visual feedback.
Designed for 2025 cutting-edge data processing with excellent UX.
"""

import polars as pl
from pathlib import Path
import time
import warnings
import fiona
import tempfile
from shapely.geometry import shape
from typing import List, Optional, Dict, Any
import os

# Rich imports for beautiful output
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.logging import RichHandler
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich import box
import logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Suppress GDAL/OGR warnings about complex polygons
os.environ['CPL_LOG'] = '/dev/null'  # Suppress GDAL C library warnings
os.environ['GDAL_DISABLE_READDIR_ON_OPEN'] = 'EMPTY_DIR'  # Performance optimization

# Initialize Rich console
console = Console()

# Set up Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(console=console, rich_tracebacks=True),
        logging.FileHandler('enhanced_gdb_conversion.log')
    ]
)
logger = logging.getLogger(__name__)

# Suppress specific GDAL/OGR warnings
logging.getLogger('fiona').setLevel(logging.ERROR)
logging.getLogger('fiona.ogrext').setLevel(logging.ERROR)
logging.getLogger('fiona._env').setLevel(logging.ERROR)

class EnhancedGDBConverter:
    """Enhanced converter with Rich UI and progress tracking."""
    
    def __init__(self, output_dir: str = "geoparquet_output"):
        """Initialize the converter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.console = console
        
        # Additional GDAL warning suppression
        self._configure_gdal_warnings()
        
        # Show startup banner
        self._show_banner()
    
    def _configure_gdal_warnings(self):
        """Configure GDAL to suppress verbose warnings."""
        try:
            from osgeo import gdal
            # Set GDAL to only show errors, not warnings
            gdal.SetConfigOption('CPL_LOG', '/dev/null')
            gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')
            gdal.PushErrorHandler('CPLQuietErrorHandler')
        except ImportError:
            # GDAL not available as Python package, environment variables should work
            pass
        
    def _show_banner(self):
        """Display a beautiful startup banner."""
        banner_text = Text()
        banner_text.append("🗺️  GDB to GeoParquet Converter", style="bold cyan")
        banner_text.append("\n")
        banner_text.append("Modern Large-Scale Geospatial Data Processing", style="italic blue")
        banner_text.append("\n")
        banner_text.append("Powered by: ", style="dim")
        banner_text.append("Polars + DuckDB + Rich", style="bold green")
        
        panel = Panel(
            banner_text,
            box=box.DOUBLE,
            padding=(1, 2),
            title="[bold magenta]Enhanced Converter[/bold magenta]",
            title_align="center"
        )
        self.console.print(panel)
        self.console.print()
        
    def _normalize_value(self, value):
        """Normalize values to handle mixed types."""
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, str):
                return value.strip() if value else None
            else:
                return str(value)
        except:
            return None
    
    def _process_chunk_enhanced(self, chunk_data: List[Dict], output_file: Path, 
                               progress: Progress, task_id: TaskID) -> bool:
        """Process chunk with enhanced progress tracking."""
        try:
            records = []
            
            # Collect all field names
            all_fields = set()
            for feature in chunk_data:
                if hasattr(feature, 'properties'):
                    properties = dict(feature.properties)
                else:
                    properties = feature.get('properties', {})
                all_fields.update(properties.keys())
            
            # Add geometry fields
            geometry_fields = ['geometry_wkt', 'geometry_type', 'geom_minx', 'geom_miny', 'geom_maxx', 'geom_maxy']
            all_fields.update(geometry_fields)
            
            # Process records with progress updates
            for i, feature in enumerate(chunk_data):
                # Initialize record
                record = {field: None for field in all_fields}
                
                # Extract properties
                if hasattr(feature, 'properties'):
                    properties = dict(feature.properties)
                else:
                    properties = feature.get('properties', {})
                
                # Normalize values
                for key, value in properties.items():
                    record[key] = self._normalize_value(value)
                
                # Handle geometry
                geometry = feature.get('geometry')
                if geometry:
                    try:
                        geom_obj = shape(geometry)
                        record['geometry_wkt'] = geom_obj.wkt
                        record['geometry_type'] = geometry.get('type', 'Unknown')
                        
                        bounds = geom_obj.bounds
                        record['geom_minx'] = str(bounds[0])
                        record['geom_miny'] = str(bounds[1])
                        record['geom_maxx'] = str(bounds[2])
                        record['geom_maxy'] = str(bounds[3])
                        
                    except Exception:
                        record['geometry_wkt'] = None
                        record['geometry_type'] = 'Error'
                        record['geom_minx'] = None
                        record['geom_miny'] = None
                        record['geom_maxx'] = None
                        record['geom_maxy'] = None
                else:
                    record['geometry_wkt'] = None
                    record['geometry_type'] = 'None'
                    record['geom_minx'] = None
                    record['geom_miny'] = None
                    record['geom_maxx'] = None
                    record['geom_maxy'] = None
                
                records.append(record)
                
                # Update progress more frequently for better time estimates
                if i % 500 == 0 and i > 0:
                    progress.update(task_id, advance=500)
            
            # Update progress for any remaining records
            remaining = len(records) % 500
            if remaining > 0:
                progress.update(task_id, advance=remaining)
            
            # Create DataFrame and save
            if records:
                df = pl.DataFrame(records, infer_schema_length=None)
                string_schema = {col: pl.Utf8 for col in df.columns}
                df = df.write_parquet(output_file, compression="snappy")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error processing chunk: {e}")
            return False
    
    def convert_layer_enhanced(self, gdb_path: str, layer_name: str, 
                              output_path: str, chunk_size: int = 15000) -> bool:
        """Convert layer with enhanced progress tracking."""
        
        with self.console.status(f"[bold green]Analyzing layer '{layer_name}'...") as status:
            try:
                with fiona.open(gdb_path, layer=layer_name) as src:
                    total_records = len(src)
                    schema = src.schema
                    crs = src.crs
            except Exception as e:
                logger.error(f"Failed to analyze layer: {e}")
                return False
        
        # Show layer info
        info_table = Table(title=f"Layer: {layer_name}")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("Records", f"{total_records:,}")
        info_table.add_row("Geometry Type", schema.get('geometry', 'Unknown'))
        info_table.add_row("CRS", str(crs) if crs else 'Unknown')
        info_table.add_row("Fields", str(len(schema.get('properties', {}))))
        
        self.console.print(info_table)
        self.console.print()
        
        # Determine processing method
        if total_records <= chunk_size:
            return self._convert_direct_enhanced(gdb_path, layer_name, output_path, total_records)
        else:
            return self._convert_streaming_enhanced(gdb_path, layer_name, output_path, chunk_size, total_records)
    
    def _convert_direct_enhanced(self, gdb_path: str, layer_name: str, 
                                output_path: str, total_records: int) -> bool:
        """Direct conversion with progress tracking."""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task(f"Converting {layer_name} (direct)", total=total_records)
            start_time = time.time()
            
            try:
                with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp_file:
                    temp_path = Path(tmp_file.name)
                
                with fiona.open(gdb_path, layer=layer_name) as src:
                    all_data = []
                    for i, feature in enumerate(src):
                        all_data.append(feature)
                        if i % 500 == 0 and i > 0:
                            progress.update(task, advance=500)
                    
                    # Process remaining records
                    remaining = len(all_data) % 500
                    if remaining > 0:
                        progress.update(task, advance=remaining)
                
                # Process all data
                chunk_task = progress.add_task("Processing data...", total=len(all_data))
                success = self._process_chunk_enhanced(all_data, temp_path, progress, chunk_task)
                
                if success:
                    temp_path.rename(output_path)
                    elapsed = time.time() - start_time
                    output_size = Path(output_path).stat().st_size / (1024 * 1024)
                    
                    # Success message
                    success_text = Text()
                    success_text.append("✅ Direct conversion completed!", style="bold green")
                    success_text.append(f"\n📊 {total_records:,} records processed in {elapsed:.2f}s")
                    success_text.append(f"\n💾 Output: {output_size:.2f} MB")
                    success_text.append(f"\n⚡ Rate: {total_records/elapsed:,.0f} records/second")
                    
                    self.console.print(Panel(success_text, title="Success", border_style="green"))
                    return True
                else:
                    if temp_path.exists():
                        temp_path.unlink()
                    return False
                    
            except Exception as e:
                logger.error(f"Direct conversion failed: {e}")
                return False
    
    def _convert_streaming_enhanced(self, gdb_path: str, layer_name: str, 
                                   output_path: str, chunk_size: int, total_records: int) -> bool:
        """Streaming conversion with enhanced progress tracking."""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task(f"Converting {layer_name} (streaming)", total=total_records)
            start_time = time.time()
            
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    with fiona.open(gdb_path, layer=layer_name) as src:
                        chunk_files = []
                        processed_records = 0
                        chunk_data = []
                        
                        for i, feature in enumerate(src):
                            chunk_data.append(feature)
                            
                            # Update main progress every 1000 records for smoother tracking
                            if (i + 1) % 1000 == 0:
                                progress.update(main_task, completed=i + 1)
                            
                            if len(chunk_data) >= chunk_size or i == total_records - 1:
                                # Process chunk
                                chunk_file = temp_path / f"chunk_{len(chunk_files):06d}.parquet"
                                chunk_task = progress.add_task(
                                    f"Processing chunk {len(chunk_files)+1}", 
                                    total=len(chunk_data)
                                )
                                
                                success = self._process_chunk_enhanced(chunk_data, chunk_file, progress, chunk_task)
                                progress.remove_task(chunk_task)
                                
                                if success:
                                    chunk_files.append(chunk_file)
                                    processed_records += len(chunk_data)
                                    progress.update(main_task, completed=processed_records)
                                
                                chunk_data = []
                        
                        # Combine chunks
                        if chunk_files:
                            combine_task = progress.add_task("Combining chunks...", total=len(chunk_files))
                            self._combine_chunks_enhanced(chunk_files, output_path, progress, combine_task)
                            
                            elapsed = time.time() - start_time
                            output_size = Path(output_path).stat().st_size / (1024 * 1024)
                            
                            # Success message
                            success_text = Text()
                            success_text.append("✅ Streaming conversion completed!", style="bold green")
                            success_text.append(f"\n📊 {processed_records:,} records processed in {elapsed:.2f}s")
                            success_text.append(f"\n🗂️  {len(chunk_files)} chunks combined")
                            success_text.append(f"\n💾 Output: {output_size:.2f} MB")
                            success_text.append(f"\n⚡ Rate: {processed_records/elapsed:,.0f} records/second")
                            
                            self.console.print(Panel(success_text, title="Success", border_style="green"))
                            return True
                        else:
                            logger.error("No chunk files created")
                            return False
                            
            except Exception as e:
                logger.error(f"Streaming conversion failed: {e}")
                return False
    
    def _combine_chunks_enhanced(self, chunk_files: List[Path], output_path: str,
                                progress: Progress, task_id: TaskID):
        """Combine chunks with progress tracking and robust schema handling."""
        try:
            # First, analyze all chunks to determine the unified schema
            unified_schema = self._determine_unified_schema(chunk_files)
            
            # Create lazy frames with consistent schema
            lazy_frames = []
            for i, chunk_file in enumerate(chunk_files):
                lf = pl.scan_parquet(str(chunk_file))
                
                # Cast all columns to String to ensure consistency
                cast_exprs = []
                for col_name, col_type in unified_schema.items():
                    if col_name in lf.columns:
                        cast_exprs.append(pl.col(col_name).cast(pl.String).alias(col_name))
                    else:
                        cast_exprs.append(pl.lit(None).cast(pl.String).alias(col_name))
                
                lf = lf.select(cast_exprs)
                lazy_frames.append(lf)
                
                progress.update(task_id, advance=1)
            
            # Concatenate and save
            combined = pl.concat(lazy_frames)
            combined.sink_parquet(output_path, compression="snappy")
            
        except Exception as e:
            logger.error(f"Failed to combine chunks: {e}")
            # Fallback method with schema normalization
            self._fallback_combine_chunks(chunk_files, output_path, progress, task_id)
    
    def _determine_unified_schema(self, chunk_files: List[Path]) -> Dict[str, str]:
        """Determine unified schema across all chunks."""
        all_columns = set()
        schema_info = {}
        
        for chunk_file in chunk_files:
            df = pl.read_parquet(str(chunk_file))
            all_columns.update(df.columns)
            
            # Track column types (prefer String over Null)
            for col in df.columns:
                col_type = str(df[col].dtype)
                if col not in schema_info or schema_info[col] == 'Null':
                    schema_info[col] = col_type
        
        # Ensure all columns default to String type
        unified_schema = {}
        for col in all_columns:
            unified_schema[col] = 'String'  # Force all to String for consistency
            
        return unified_schema
    
    def _fallback_combine_chunks(self, chunk_files: List[Path], output_path: str,
                                progress: Progress, task_id: TaskID):
        """Fallback method with explicit schema normalization."""
        all_data = []
        all_columns = set()
        
        # First pass: collect all columns
        for chunk_file in chunk_files:
            df = pl.read_parquet(str(chunk_file))
            all_columns.update(df.columns)
        
        # Second pass: normalize schemas and collect data
        for chunk_file in chunk_files:
            df = pl.read_parquet(str(chunk_file))
            
            # Add missing columns as null strings
            for col in all_columns:
                if col not in df.columns:
                    df = df.with_columns(pl.lit(None).cast(pl.String).alias(col))
            
            # Cast all columns to String
            cast_exprs = [pl.col(col).cast(pl.String) for col in all_columns]
            df = df.select(cast_exprs)
            
            all_data.append(df)
            progress.update(task_id, advance=1)
        
        if all_data:
            combined = pl.concat(all_data, how="vertical")
            combined.write_parquet(output_path, compression="snappy")
    
    def convert_gdb_enhanced(self, gdb_path: str, layers: Optional[List[str]] = None,
                            chunk_size: int = 15000) -> Dict[str, Any]:
        """Convert GDB with enhanced UI."""
        gdb_path = Path(gdb_path)
        
        # Show GDB header
        gdb_text = Text(f"🗃️  {gdb_path.name}", style="bold yellow")
        gdb_panel = Panel(gdb_text, title="Processing GDB", border_style="yellow")
        self.console.print(gdb_panel)
        
        try:
            available_layers = fiona.listlayers(str(gdb_path))
        except Exception as e:
            logger.error(f"Cannot list layers: {e}")
            return {'error': str(e)}
        
        if layers:
            layers_to_convert = [layer for layer in layers if layer in available_layers]
        else:
            layers_to_convert = available_layers
        
        # Show layers to convert
        layer_table = Table(title="Layers to Convert")
        layer_table.add_column("Layer", style="cyan")
        layer_table.add_column("Status", style="white")
        
        for layer in layers_to_convert:
            layer_table.add_row(layer, "⏳ Pending")
        
        self.console.print(layer_table)
        self.console.print()
        
        # Create output directory
        gdb_output_dir = self.output_dir / gdb_path.stem
        gdb_output_dir.mkdir(exist_ok=True)
        
        results = {
            'gdb_path': str(gdb_path),
            'output_dir': str(gdb_output_dir),
            'layers_converted': [],
            'layers_failed': [],
            'total_time': 0
        }
        
        total_start_time = time.time()
        
        # Convert each layer
        for i, layer_name in enumerate(layers_to_convert):
            self.console.print(f"\n[bold blue]Processing Layer {i+1}/{len(layers_to_convert)}[/bold blue]")
            
            output_file = gdb_output_dir / f"{layer_name}.parquet"
            
            success = self.convert_layer_enhanced(
                str(gdb_path), layer_name, str(output_file), chunk_size
            )
            
            if success:
                # Get record count for results
                try:
                    with fiona.open(str(gdb_path), layer=layer_name) as src:
                        record_count = len(src)
                except:
                    record_count = 0
                    
                results['layers_converted'].append({
                    'layer': layer_name,
                    'output_file': str(output_file),
                    'record_count': record_count
                })
            else:
                results['layers_failed'].append(layer_name)
        
        results['total_time'] = time.time() - total_start_time
        
        # Show final summary
        self._show_gdb_summary(gdb_path.name, results)
        
        return results
    
    def _show_gdb_summary(self, gdb_name: str, results: Dict[str, Any]):
        """Show beautiful summary for GDB conversion."""
        
        summary_table = Table(title=f"Summary: {gdb_name}")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        successful = len(results['layers_converted'])
        failed = len(results['layers_failed'])
        total_time = results['total_time']
        
        summary_table.add_row("✅ Layers Converted", str(successful))
        summary_table.add_row("❌ Layers Failed", str(failed))
        summary_table.add_row("⏱️  Total Time", f"{total_time:.2f} seconds")
        
        if successful > 0:
            total_records = sum(layer['record_count'] for layer in results['layers_converted'])
            summary_table.add_row("📊 Total Records", f"{total_records:,}")
            if total_time > 0:
                summary_table.add_row("⚡ Processing Rate", f"{total_records/total_time:,.0f} records/sec")
        
        self.console.print(summary_table)
        self.console.print()

def main():
    """Enhanced main function with Rich UI."""
    converter = EnhancedGDBConverter()
    
    # Find GDB files
    current_dir = Path(".")
    gdb_files = [f for f in current_dir.iterdir() if f.is_dir() and f.name.endswith('.gdb')]
    
    if not gdb_files:
        console.print("[bold red]❌ No .gdb files found in current directory[/bold red]")
        return
    
    # Show discovered files
    file_tree = Tree("🔍 Discovered GDB Files")
    for gdb in gdb_files:
        file_tree.add(f"📁 {gdb.name}")
    
    console.print(file_tree)
    console.print()
    
    # Convert each GDB
    all_results = []
    total_start_time = time.time()
    
    with console.status("[bold green]Starting conversion process..."):
        time.sleep(1)  # Brief pause for dramatic effect
    
    for i, gdb_file in enumerate(gdb_files):
        console.print(f"\n[bold magenta]═══ GDB {i+1}/{len(gdb_files)} ═══[/bold magenta]")
        result = converter.convert_gdb_enhanced(str(gdb_file), chunk_size=15000)
        all_results.append(result)
    
    total_elapsed = time.time() - total_start_time
    
    # Final summary
    console.print(f"\n[bold green]🎉 CONVERSION COMPLETE! 🎉[/bold green]")
    
    final_table = Table(title="Final Results", box=box.DOUBLE)
    final_table.add_column("Metric", style="bold cyan")
    final_table.add_column("Value", style="bold white")
    
    total_successful = sum(len(r.get('layers_converted', [])) for r in all_results)
    total_failed = sum(len(r.get('layers_failed', [])) for r in all_results)
    total_records = sum(
        sum(layer['record_count'] for layer in r.get('layers_converted', []))
        for r in all_results
    )
    
    final_table.add_row("🎯 Total Layers Converted", str(total_successful))
    final_table.add_row("💥 Total Layers Failed", str(total_failed))
    final_table.add_row("📊 Total Records Processed", f"{total_records:,}")
    final_table.add_row("⏱️  Total Processing Time", f"{total_elapsed:.2f} seconds")
    if total_records > 0 and total_elapsed > 0:
        final_table.add_row("⚡ Average Processing Rate", f"{total_records/total_elapsed:,.0f} records/sec")
    
    console.print(final_table)
    
    # Show output structure
    console.print(f"\n[bold blue]📂 Output Directory: {converter.output_dir}[/bold blue]")
    
    output_tree = Tree("📁 Output Structure")
    total_size_mb = 0
    
    for item in converter.output_dir.rglob("*.parquet"):
        size_mb = item.stat().st_size / (1024 * 1024)
        total_size_mb += size_mb
        
        relative_path = item.relative_to(converter.output_dir)
        output_tree.add(f"📄 {relative_path} ({size_mb:.2f} MB)")
    
    console.print(output_tree)
    console.print(f"\n[bold green]💾 Total Output Size: {total_size_mb:.2f} MB[/bold green]")
    
    # Compression estimate
    if total_size_mb > 0 and total_records > 0:
        estimated_original_gb = total_records * 0.002
        if estimated_original_gb > 0:
            compression_ratio = (estimated_original_gb * 1024) / total_size_mb
            console.print(f"[bold yellow]🗜️  Estimated Compression Ratio: {compression_ratio:.1f}x[/bold yellow]")

if __name__ == "__main__":
    main() 