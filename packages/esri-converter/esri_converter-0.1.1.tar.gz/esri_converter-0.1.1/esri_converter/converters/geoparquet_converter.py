#!/usr/bin/env python3
"""
GeoParquet-compliant converter for ESRI GDB files.
Produces valid GeoParquet files according to the OGC GeoParquet specification.
"""

import json
import logging
import os
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any

import fiona
import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq
from rich import box

# Rich imports for beautiful output
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text
from shapely.geometry import shape

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Suppress GDAL/OGR warnings about complex polygons
os.environ["CPL_LOG"] = "/dev/null"
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"

# Initialize Rich console
console = Console()

# Set up Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(console=console, rich_tracebacks=True),
        logging.FileHandler("geoparquet_conversion.log"),
    ],
)
logger = logging.getLogger(__name__)

# Suppress specific GDAL/OGR warnings
logging.getLogger("fiona").setLevel(logging.ERROR)
logging.getLogger("fiona.ogrext").setLevel(logging.ERROR)
logging.getLogger("fiona._env").setLevel(logging.ERROR)


class GeoParquetConverter:
    """Converter that produces OGC GeoParquet-compliant files."""

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

            gdal.SetConfigOption("CPL_LOG", "/dev/null")
            gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
            gdal.PushErrorHandler("CPLQuietErrorHandler")
        except ImportError:
            pass

    def _show_banner(self):
        """Display a beautiful startup banner."""
        banner_text = Text()
        banner_text.append("🗺️  GDB to GeoParquet Converter", style="bold cyan")
        banner_text.append("\n")
        banner_text.append("OGC GeoParquet-Compliant Output", style="italic blue")
        banner_text.append("\n")
        banner_text.append("Powered by: ", style="dim")
        banner_text.append("GeoPandas + Polars + Rich", style="bold green")

        panel = Panel(
            banner_text,
            box=box.DOUBLE,
            padding=(1, 2),
            title="[bold magenta]GeoParquet Converter[/bold magenta]",
            title_align="center",
        )
        self.console.print(panel)
        self.console.print()

    def _process_chunk_geoparquet(
        self,
        chunk_data: list[dict],
        crs: Any,
        progress: Progress | None = None,
        task_id: TaskID | None = None,
    ) -> gpd.GeoDataFrame:
        """Process chunk into a proper GeoDataFrame."""
        try:
            records = []
            geometries = []

            for i, feature in enumerate(chunk_data):
                # Extract properties
                if hasattr(feature, "properties"):
                    properties = dict(feature.properties)
                else:
                    properties = feature.get("properties", {})

                # Extract geometry
                geometry = feature.get("geometry")
                if geometry:
                    try:
                        geom_obj = shape(geometry)
                        geometries.append(geom_obj)
                    except Exception:
                        geometries.append(None)
                else:
                    geometries.append(None)

                records.append(properties)

                # Update progress
                if progress and task_id and i % 500 == 0 and i > 0:
                    progress.update(task_id, advance=500)

            # Update progress for remaining records
            if progress and task_id:
                remaining = len(records) % 500
                if remaining > 0:
                    progress.update(task_id, advance=remaining)

            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(records, geometry=geometries, crs=crs)
            return gdf

        except Exception as e:
            logger.error(f"Error processing chunk: {e}")
            raise

    def convert_layer_geoparquet(
        self, gdb_path: str, layer_name: str, output_path: str, chunk_size: int = 15000
    ) -> bool:
        """Convert layer to proper GeoParquet format."""

        with self.console.status(f"[bold green]Analyzing layer '{layer_name}'..."):
            try:
                with fiona.open(gdb_path, layer=layer_name) as src:
                    total_records = len(src)
                    schema = src.schema
                    crs = src.crs
                    bounds = src.bounds
            except Exception as e:
                logger.error(f"Failed to analyze layer: {e}")
                return False

        # Show layer info
        info_table = Table(title=f"Layer: {layer_name}")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Records", f"{total_records:,}")
        info_table.add_row("Geometry Type", schema.get("geometry", "Unknown"))
        info_table.add_row("CRS", str(crs) if crs else "Unknown")
        info_table.add_row("Fields", str(len(schema.get("properties", {}))))
        info_table.add_row("Bounds", f"{bounds}" if bounds else "Unknown")

        self.console.print(info_table)
        self.console.print()

        # Determine processing method
        if total_records <= chunk_size:
            return self._convert_direct_geoparquet(
                gdb_path, layer_name, output_path, total_records, crs
            )
        else:
            return self._convert_streaming_geoparquet(
                gdb_path, layer_name, output_path, chunk_size, total_records, crs
            )

    def _convert_direct_geoparquet(
        self, gdb_path: str, layer_name: str, output_path: str, total_records: int, crs: Any
    ) -> bool:
        """Direct conversion to GeoParquet."""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Converting {layer_name} (direct)", total=total_records)
            start_time = time.time()

            try:
                # Read all features
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

                # Process all data into GeoDataFrame
                process_task = progress.add_task("Creating GeoDataFrame...", total=len(all_data))
                gdf = self._process_chunk_geoparquet(all_data, crs, progress, process_task)

                # Save as GeoParquet
                save_task = progress.add_task("Writing GeoParquet...", total=1)
                gdf.to_parquet(output_path, compression="snappy")
                progress.update(save_task, advance=1)

                elapsed = time.time() - start_time
                output_size = Path(output_path).stat().st_size / (1024 * 1024)

                # Verify it's a valid GeoParquet
                self._verify_geoparquet(output_path)

                # Success message
                success_text = Text()
                success_text.append("✅ GeoParquet conversion completed!", style="bold green")
                success_text.append(f"\n📊 {total_records:,} records processed in {elapsed:.2f}s")
                success_text.append(f"\n💾 Output: {output_size:.2f} MB")
                success_text.append(f"\n⚡ Rate: {total_records / elapsed:,.0f} records/second")
                success_text.append(f"\n🗺️  CRS: {crs}")

                self.console.print(Panel(success_text, title="Success", border_style="green"))
                return True

            except Exception as e:
                logger.error(f"Direct conversion failed: {e}")
                return False

    def _convert_streaming_geoparquet(
        self,
        gdb_path: str,
        layer_name: str,
        output_path: str,
        chunk_size: int,
        total_records: int,
        crs: Any,
    ) -> bool:
        """Streaming conversion to GeoParquet with chunk processing."""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            main_task = progress.add_task(
                f"Converting {layer_name} (streaming)", total=total_records
            )
            start_time = time.time()

            try:
                with tempfile.TemporaryDirectory():
                    with fiona.open(gdb_path, layer=layer_name) as src:
                        chunk_gdfs = []
                        processed_records = 0
                        chunk_data = []

                        for i, feature in enumerate(src):
                            chunk_data.append(feature)

                            # Update main progress
                            if (i + 1) % 1000 == 0:
                                progress.update(main_task, completed=i + 1)

                            if len(chunk_data) >= chunk_size or i == total_records - 1:
                                # Process chunk
                                chunk_task = progress.add_task(
                                    f"Processing chunk {len(chunk_gdfs) + 1}", total=len(chunk_data)
                                )

                                gdf_chunk = self._process_chunk_geoparquet(
                                    chunk_data, crs, progress, chunk_task
                                )
                                chunk_gdfs.append(gdf_chunk)
                                progress.remove_task(chunk_task)

                                processed_records += len(chunk_data)
                                progress.update(main_task, completed=processed_records)

                                chunk_data = []

                        # Combine chunks
                        if chunk_gdfs:
                            combine_task = progress.add_task(
                                "Combining chunks...", total=len(chunk_gdfs)
                            )

                            # Concatenate all GeoDataFrames
                            combined_gdf = pd.concat(chunk_gdfs, ignore_index=True)
                            # Ensure it's a proper GeoDataFrame with correct CRS
                            combined_gdf = gpd.GeoDataFrame(combined_gdf, crs=crs)

                            progress.update(combine_task, advance=len(chunk_gdfs))

                            # Save as GeoParquet
                            save_task = progress.add_task("Writing GeoParquet...", total=1)
                            combined_gdf.to_parquet(output_path, compression="snappy")
                            progress.update(save_task, advance=1)

                            elapsed = time.time() - start_time
                            output_size = Path(output_path).stat().st_size / (1024 * 1024)

                            # Verify it's a valid GeoParquet
                            self._verify_geoparquet(output_path)

                            # Success message
                            success_text = Text()
                            success_text.append(
                                "✅ GeoParquet streaming conversion completed!", style="bold green"
                            )
                            success_text.append(
                                f"\n📊 {processed_records:,} records processed in {elapsed:.2f}s"
                            )
                            success_text.append(f"\n🗂️  {len(chunk_gdfs)} chunks combined")
                            success_text.append(f"\n💾 Output: {output_size:.2f} MB")
                            success_text.append(
                                f"\n⚡ Rate: {processed_records / elapsed:,.0f} records/second"
                            )
                            success_text.append(f"\n🗺️  CRS: {crs}")

                            self.console.print(
                                Panel(success_text, title="Success", border_style="green")
                            )
                            return True
                        else:
                            logger.error("No chunks created")
                            return False

            except Exception as e:
                logger.error(f"Streaming conversion failed: {e}")
                return False

    def _verify_geoparquet(self, file_path: str) -> bool:
        """Verify that the output is a valid GeoParquet file."""
        try:
            # Check if it can be read as GeoParquet
            gpd.read_parquet(file_path)

            # Check for geo metadata
            pq_file = pq.ParquetFile(file_path)
            metadata = pq_file.metadata

            if metadata.metadata and b"geo" in metadata.metadata:
                geo_metadata = json.loads(metadata.metadata[b"geo"].decode("utf-8"))
                logger.info(f"GeoParquet metadata found: {geo_metadata.get('version', 'unknown')}")
                return True
            else:
                logger.warning("No geo metadata found in parquet file")
                return False

        except Exception as e:
            logger.error(f"GeoParquet verification failed: {e}")
            return False

    def convert_gdb_geoparquet(
        self, gdb_path: str, layers: list[str] | None = None, chunk_size: int = 15000
    ) -> dict[str, Any]:
        """Convert GDB to GeoParquet format."""
        gdb_path = Path(gdb_path)

        # Show GDB header
        gdb_text = Text(f"🗃️  {gdb_path.name}", style="bold yellow")
        gdb_panel = Panel(gdb_text, title="Processing GDB", border_style="yellow")
        self.console.print(gdb_panel)

        try:
            available_layers = fiona.listlayers(str(gdb_path))
        except Exception as e:
            logger.error(f"Cannot list layers: {e}")
            return {"error": str(e)}

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
            "gdb_path": str(gdb_path),
            "output_dir": str(gdb_output_dir),
            "layers_converted": [],
            "layers_failed": [],
            "total_time": 0,
        }

        total_start_time = time.time()

        # Convert each layer
        for i, layer_name in enumerate(layers_to_convert):
            self.console.print(
                f"\n[bold blue]Processing Layer {i + 1}/{len(layers_to_convert)}[/bold blue]"
            )

            output_file = gdb_output_dir / f"{layer_name}.parquet"

            success = self.convert_layer_geoparquet(
                str(gdb_path), layer_name, str(output_file), chunk_size
            )

            if success:
                # Get record count and CRS for results
                try:
                    with fiona.open(str(gdb_path), layer=layer_name) as src:
                        record_count = len(src)
                        crs = src.crs
                except Exception:
                    record_count = 0
                    crs = None

                results["layers_converted"].append(
                    {
                        "layer": layer_name,
                        "output_file": str(output_file),
                        "record_count": record_count,
                        "crs": str(crs) if crs else None,
                    }
                )
            else:
                results["layers_failed"].append(layer_name)

        results["total_time"] = time.time() - total_start_time

        # Show final summary
        self._show_gdb_summary(gdb_path.name, results)

        return results

    def _show_gdb_summary(self, gdb_name: str, results: dict[str, Any]):
        """Show beautiful summary for GDB conversion."""

        summary_table = Table(title=f"Summary: {gdb_name}")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")

        successful = len(results["layers_converted"])
        failed = len(results["layers_failed"])
        total_time = results["total_time"]

        summary_table.add_row("✅ Layers Converted", str(successful))
        summary_table.add_row("❌ Layers Failed", str(failed))
        summary_table.add_row("⏱️  Total Time", f"{total_time:.2f} seconds")

        if successful > 0:
            total_records = sum(layer["record_count"] for layer in results["layers_converted"])
            summary_table.add_row("📊 Total Records", f"{total_records:,}")
            if total_time > 0:
                summary_table.add_row(
                    "⚡ Processing Rate", f"{total_records / total_time:,.0f} records/sec"
                )

        self.console.print(summary_table)
        self.console.print()
