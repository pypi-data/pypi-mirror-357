# -*- coding: utf-8 -*-
"""
main.py

ScodaKit: A scientific Python-based command line toolkit for S-coda seismic wave analysis and scattering parameters estimation

This script orchestrates the complete S-coda wave analysis and scattering parameters estimation process,
including:
    1. Downloading waveform data
    2. Manual picking of P/S phases
    3. Merging picks with event metadata
    4. Generating maps of events and stations
    5. Extracting and analyzing S-coda waveforms
    6. Visualizing results

Usage:
    scodakit --download --pick --merge_catalog --map --process --plot 

Author: Marios Karagiorgas
"""

import argparse
import logging
import sys
import time
from pathlib import Path
import json
import yaml

from scodakit.download import download_waveforms
from scodakit.picking import pick_phases_from_folder
from scodakit.merge_catalogue import prepare_catalog_for_mfp
from scodakit.map_generator import generate_map
from scodakit.process import process_event_batch
from scodakit.plots import plot_all

# Check python version compatibility
if sys.version_info.major < 3 or sys.version_info.minor < 8:
    print("Python version 3.8 or higher is required.")
    print(f"Current version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("Please update your Python version.")
    print("Exiting...")
    sys.exit(1)

# Redirects print statements and stdout to both console and a log file.
class DualLogger:
    """Redirect print and stdout to both console and file."""
    def __init__(self, logfile_path):
        self.terminal = sys.stdout
        self.log = open(logfile_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Sets up logging to both console and file. If log_to_file is True, it will also redirect stdout to a file
def setup_logging(output_dir: Path, log_to_file: bool = True):
    """Sets up console and optional file logging."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = output_dir / "pipeline.log"
    
    # Console formatter: just the message
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(levelname)s- %(message)s'))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler]
    )

    # If file logging enabled, redirect stdout (print) and also attach a file handler to logging
    if log_to_file:
        # Redirect print() to file
        sys.stdout = DualLogger(log_file)

        # Add file handler to logging module
        file_handler = logging.FileHandler(log_file, mode='a', encoding="utf-8")
        # Only level and message, no acttime
        file_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)

        logging.info("Logging to file enabled.")

# Check for required dependencies
def check_dependencies():
    try:
        import obspy
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import sklearn
        import geopandas as gpd
        import cartopy
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature
        import json
        import yaml

    except ImportError as e:
        logging.error(f"Missing dependency: {e.name}. Install it using pip.")
        return False
    return True

def log_stage(name):
    print(f"\n{'='*50}\n Starting Stage: {name}\n{'='*50}")
    return time.time()

def log_stage_complete(start_time, stage_name):
    duration = time.time() - start_time
    logging.info(f"{stage_name} completed in {duration:.1f} seconds.")

def main():
    pipeline_start = time.time()
    parser = argparse.ArgumentParser(
        description="Scodakit: A scientific Python-based command line toolkit for S-coda seismic wave analysis and scattering parameters estimation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog= "For more information, please visit https://github.com/marioskaragiorgas/ScodaKit#readme"
    )

    try:


        # Pipeline stages
        stages = parser.add_argument_group("Pipeline Stages")
        stages.add_argument('-dr', '--dry_run', action='store_true', help="Dry run mode. Validate arguments and configuration without executing pipeline stages")
        stages.add_argument('-a', '--all', action='store_true', help="Run all stages of the pipeline")
        stages.add_argument('-d', '--download', action='store_true', help="Download waveforms from FDSN")
        stages.add_argument('-p', '--pick', action='store_true', help="Manually pick P and S arrivals")
        stages.add_argument('-me', '--merge_catalog', action='store_true', help="Merge picks with seismic metadata")
        stages.add_argument('-ma', '--map', action='store_true', help="Create GIS-compatible maps and export event/station data")
        stages.add_argument('-pr', '--process', action='store_true', help="Extract S-coda and compute mean free path")
        stages.add_argument('-pl', '--plot', action='store_true', help="Plot waveforms")

        # Downloading options
        download_group = parser.add_argument_group("Download Options")
        
        download_group.add_argument('--catalog', type=str, help="Seismic event catalog file (.xml, .csv, .xlsx). If not provided, the pipeline will not download waveforms and the pipeline will not run.")
        download_group.add_argument('--stations', nargs='+', default=None, help="Station codes or a single station code as a string. A station code contains the network code and the station name (e.g., 'HL.ATH' or 'HL.ATH','HA.ATHU'). If a single station code is provided, it will be used to download waveforms for that station only. If multiple stations are provided, they will be used to download waveforms for all specified stations.")
        download_group.add_argument('--bbox', type= str, default=None, help="Bounding Box (Lat/Lon limits). A rectangular area to search for available stations using minlatitude, maxlatitude, minlongitude, and maxlongitude in the format: 'minlat,minlon,maxlat,maxlon'.")
        download_group.add_argument('--radius', type=float, default=None, help="Radius in kilometers to search for stations. If not set, station_list or bounding box must be provided.") 
        download_group.add_argument('--channels',  type=str, default="HH?", help="SEED channel pattern (e.g., HH?). Default is 'HH?'. Use '?' as a wildcard for any character. If not set, all channels will be downloaded.")  
        download_group.add_argument('--start_offset', type=int, default=-30, help="Seconds before origin. Default is -30 seconds. Note that this is the total length of the waveform, not the start time relative to the origin.")
        download_group.add_argument('--end_offset', type=int, default=150, help="Seconds after origin. Default is 150 seconds. Note that this is the total length of the waveform, not the end time relative to the origin.")        
        download_group.add_argument('--output_format', type=str, default="MSEED", help="Waveform format. Options: MSEED, SAC, WAV. Default is MSEED. Note that SAC and SEGY formats are not supported by FDSN web services.")        
        download_group.add_argument('--node', type=str, default="NOA", help="FDSN data node. Available nodes can be found in obspy.clients.fdsn.header.URL_MAPPINGS.")       
        download_group.add_argument('--network_filter', nargs='+', default=["*"], help="Allowed network codes. Use '*' for all networks. Multiple networks can be specified as a list (e.g., --network_filter 'HL','GR')")
        download_group.add_argument('--threads', type=int, default=1, help="Number of CPU threads to use for parallel downloading of waveforms. Default is 1 (single-threaded).")

        # Map Generation options
        map_group = parser.add_argument_group("Map Generation Options")
        map_group.add_argument('--map_output_dir', type=str, default="maps", help="Output directory for maps. Will be created if it doesn't exist.")
        map_group.add_argument('--image_formats', nargs='+', choices= ["png", "pdf"], default=["png", "pdf"], help="Image formats for map output")
        map_group.add_argument('--export_formats', nargs='+', choices=["geojson", "csv", "shp"], default=["geojson", "csv", "shp"], help="Export formats for map data (e.g., geojson, csv, shapefile)")

        # General
        general_group = parser.add_argument_group("General Options")
        general_group.add_argument('--output_dir', type=str, default=None, help="Base output directory containing the results specified by the user. Will be created if it doesn't exist. If not set, the pipeline will not run.")
        general_group.add_argument('--log', action='store_true', help="Also write logs to pipeline.log")
        general_group.add_argument('--config', type=str, default=None, help="Path to config file (.json or .yaml). If provided, it will override command line arguments.")

        args = parser.parse_args()
        
        # If a config file is provided, load it and update args
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                logging.error(f"Config file not found: {args.config}")
                sys.exit(1)
            if config_path.suffix in ['.json', '.yaml', '.yml']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.suffix == '.json':
                        config_data = json.load(f)
                    else:
                        config_data = yaml.safe_load(f)
                # Update args with config data
                for key, value in config_data.items():
                    if hasattr(args, key):
                        setattr(args, key, value)
                        print(f"Overriding argument '{key}' with value from config: {value}")
                    else:
                        logging.warning(f"Config key '{key}' not recognized. Skipping.")
            else:
                logging.error(f"Unsupported config file format: {config_path.suffix}. Supported formats are .json and .yaml")

        # If dry_run is set, validate arguments and exit
        if args.dry_run:
            logging.info("Dry run mode enabled. Validating arguments and configuration without executing pipeline stages.")
            logging.info(f"Pipeline arguments:\n{json.dumps(vars(args), indent=2)}") 
            sys.exit(0)

        # If -a or --all is set, enable all stages
        if args.all:
            args.download = True
            args.pick = True
            args.merge_catalog = True
            args.map = True
            args.process = True
            args.plot = True

        # Validate and process output directory
        if not args.output_dir:
            logging.error("Output directory must be specified using --output_dir")
            sys.exit(1)
        
        output_dir = Path(args.output_dir) / 'results'
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        setup_logging(output_dir, args.log)

        logging.info("S-coda Mean Free Path Pipeline started.")
        logging.info(f"Working directory: {output_dir}")
        logging.info(f"User arguments: {args}")

        if not check_dependencies():
            sys.exit(1)

        if (args.download or args.merge_catalog) and not Path(args.catalog).exists():
            logging.error(f"Catalog file not found: {args.catalog}")
            sys.exit(1)

        # STAGE 1: Download
        if args.download:

            if args.bbox:
                try:
                    minlat, minlon, maxlat, maxlon = map(float, args.bbox.split(','))
                except ValueError:
                    raise ValueError("Bounding box must have four comma-separated float values.")
            else:
                minlat, minlon, maxlat, maxlon = (None, None, None, None)

            start = log_stage("Downloading Waveforms")
            download_waveforms(
                catalogue_path=args.catalog,
                station_list=args.stations, #if not (len(args.stations) == 1 and args.stations[0].isdigit()) else None,
                radius=args.radius,
                bbox=[minlat, minlon, maxlat, maxlon],
                channels=args.channels,
                start_offset=args.start_offset,
                end_offset=args.end_offset,
                output_format=args.output_format,
                node=args.node,
                network_filter=args.network_filter,
                destination=output_dir / "waveforms",
                threads=args.threads
            )
            log_stage_complete(start, "Download")
        else:
            logging.info("Skipping download stage (-download not set)")

        # STAGE 2: Pick Phases
        if args.pick:
            start = log_stage("Manual P/S Phase Picking")
            pick_phases_from_folder(
                input_folder=str(output_dir / "waveforms"),
                output_excel=str(output_dir / "arrival_times.xlsx"),
                output_waveform_folder=str(output_dir / "validated_waveforms")
            )
            log_stage_complete(start, "Picking")
        else:
            logging.info("Skipping picking stage (-pick not set)")

        # STAGE 3: Merge Catalog
        if args.merge_catalog:
            start = log_stage("Merging Picks with Catalog")
            prepare_catalog_for_mfp(
                picks_excel=str(output_dir / "arrival_times.xlsx"),
                seismic_catalog=args.catalog,
                output_excel=str(output_dir / "merged_catalog.xlsx"),
                client=args.node
            )
            log_stage_complete(start, "Merge Catalog")
        else:
            logging.info("Skipping merge_catalog stage (-merge_catalog not set)")

        # STAGE 4: Generate Map
        if args.map:
            start = log_stage("Generating Map")
            generate_map(
                catalogue_path=str(output_dir / "merged_catalog.xlsx"),
                output_dir=str(output_dir / args.map_output_dir),
                image_formats=args.image_formats,
                export_formats=args.export_formats
            )
            log_stage_complete(start, "Map Generation")
        else:
            logging.info("Skipping map generation stage (-map not set)")

        # STAGE 5: Process
        if args.process:
            start = log_stage("S-Coda Mean Free Path Estimation")
            process_event_batch(
                data_catalog=str(output_dir / "merged_catalog.xlsx"),
                waveform_dir=str(output_dir / "validated_waveforms"),
                output_dir=str(output_dir / "processed_output")
            )
            log_stage_complete(start, "Processing")
        else:
            logging.info("Skipping processing stage (-process not set)")

        # STAGE 6: Plot
        if args.plot:
            start = log_stage("Plotting")
            plot_all(
                arrival_excel=str(output_dir / "arrival_times.xlsx"),
                validated_waveforms_dir=str(output_dir / "validated_waveforms"),
                coda_waveforms_dir=str(output_dir / "processed_output" / "coda_segments"),
                output_full_dir=str(output_dir / "plots/full_waveforms"),
                output_coda_dir=str(output_dir / "plots/coda_waveforms")
            )
            log_stage_complete(start, "Plotting")
        else:
            logging.info("Skipping plotting stage (-plot not set)")

        logging.info("Pipeline execution complete. All selected stages finished.")
        logging.info(f"Total execution time: {time.time() - pipeline_start:.1f} seconds.")
        logging.info("Exiting pipeline.")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error("Pipeline execution failed.")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logging.warning("Pipeline execution interrupted by user.")
        # Save partial results if needed and clean up
        
        logging.info("Exiting pipeline.")
        sys.exit(0)

if __name__ == "__main__":
    main()
