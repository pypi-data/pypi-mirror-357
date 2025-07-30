# -*- coding: utf-8 -*-
"""
download.py

Downloads seismic waveforms from a catalog using ObsPy, with flexible station selection
(either by station codes list or radius) and multiple waveform output formats (MSEED, SAC, WAV).

Author: Marios Karagiorgas
"""

from obspy import UTCDateTime, read_events
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import URL_MAPPINGS
from obspy.geodetics.base import kilometer2degrees
from pathlib import Path
import logging
import pandas as pd
from typing import List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def detect_delimiter(filepath):
    """
    Detects the delimiter of a CSV or TXT file by reading the first few lines.
    Args:
        filepath (str): Path to the file.
    Returns:
        str: Detected delimiter (comma or tab).
    """
    try:
        with open(filepath, 'r') as file:
            lines = [file.readline() for _ in range(5)]
        comma_count = sum(line.count(',') for line in lines)
        tab_count = sum(line.count('\t') for line in lines)
        return ',' if comma_count > tab_count else '\t'
    except Exception as e:
        logging.error(f"Error detecting delimiter: {e}")
        return ','

def get_inventory_stations(inv):
    """
    Extracts station codes from an ObsPy inventory object.
    Args:
        inv (obspy.core.inventory.Inventory): ObsPy inventory object.
    Returns:
        List[str]: List of station codes in the format 'NET.STA.CHA'.
    """
    code_list = []
    for net in inv:
        for sta in net:
                code_list.append(f"{net.code}.{sta.code}")
    return sorted(code_list)

def fetch_waveform_for_station(node, code, event, start_offset, end_offset, channels):
    """
    Fetches waveform data for a specific station and event.
    Args:
        node(obspy.clients.fdsn.Client): ObsPy FDSN client node.
        code (str): Station code in the format 'NET.STA'.
        event (UTCDateTime): Event time.
        start_offset (int): Start time offset in seconds before the event.
        end_offset (int): End time offset in seconds after the event.
        channels (str): Channel codes to download.
    Returns:
        obspy.core.stream.Stream: ObsPy Stream object containing the waveform data.
    """
    try:
        logging.info(f"Fetching waveform for {code} at {event}")
        
        if not isinstance(event, UTCDateTime):
            raise ValueError("Event must be an instance of UTCDateTime.")
        
        if not isinstance(start_offset, int) or not isinstance(end_offset, int):
            raise ValueError("Start and end offsets must be integers.")
        
        if not isinstance(channels, str):
            raise ValueError("Channels must be a string representing channel codes (e.g., '*', 'BHZ', etc.).")
        
        if not code or "." not in code:
            raise ValueError("Invalid station code format. Expected 'NET.STA'.")
        
        # Split the code into network and station
        net, sta = code.split(".")[:2]  # Split the code into network and station
        wf = node.get_waveforms(
            network=net, station=sta, channel=channels, location="*",
            starttime=event + start_offset, endtime=event + end_offset,
            attach_response=True
        )
        return wf
    except Exception as e:
        logging.warning(f"Failed to fetch waveform for {code} at {event}: {e}")
        return None
    
def make_event_folders(events, destination):
    """
    Creates a directory structure for each event based on its date.
    Args:
        events (list): List of event times (UTCDateTime).
        destination (str): Base directory for event folders.
    Returns:
        dict: Dictionary mapping event times to their respective directory paths.
    """
    destination = Path(destination)
    path_dict = {}
    for event in events:
        event_dir = destination / str(event.year)
        event_dir.mkdir(parents=True, exist_ok=True)
        path_dict[str(event)] = event_dir
    return path_dict

def write_waveform(wf, out_path, output_format):
    """
    Safely writes a waveform to disk in the specified format.
    Applies basic preprocessing if supported.
    Args:
        wf (obspy.core.stream.Stream): ObsPy Stream object.
        out_path (Path): Output file path.
        output_format (str): Format to save in ("MSEED", "SAC", or "WAV").
    """
    try:
        if len(wf) == 0:
            logging.warning("Empty waveform stream — skipping write.")
            return

        # Remove response only if channels are present
        if output_format.upper() in ["SAC", "WAV", "MSEED"]:
            wf.remove_response(output="VEL", water_level=60, zero_mean=True, taper=True, taper_fraction=0.05)
            wf.merge()
        else:
            logging.warning(f"Unsupported output format: {output_format}")
            return

        # Sanity check for trace metadata
        for tr in wf:
            if not all([tr.stats.get(k) for k in ["network", "station", "channel", "starttime"]]):
                logging.warning(f"Missing metadata in trace: {tr.stats} — skipping write.")
                return

        wf.detrend("linear")
        wf.detrend("demean")
        out_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure path exists
        wf.write(str(out_path), format=output_format.upper())
        logging.info(f"Waveform saved to {out_path}")

    except Exception as e:
        logging.warning(f"Failed to save waveform {out_path.name}: {e}")

def download_waveforms(
    catalogue_path: Union[str, Path], # Path to the catalogue file. Can be XML, CSV, TXT, XLSX. 
    station_list: Union[str, List[str], None], # List of station codes in the format 'NET.STA.CHA' or None. If None, stations will be selected based on radius. If a string provided, it will be treated as a single station code.
    destination: Union[str, Path], # Directory to save the downloaded waveforms.
    bbox:  Union[list[float], None], # Bounding box in the format [min_lon, min_lat, max_lon, max_lat]. If None, no bounding box is applied.
    radius: Union[float, None] = None, # Radius in kilometers to search for stations. If None, station_list must be provided.
    channels: str = "*", # Channel codes to download. Default is all channels.
    start_offset: int = -30, # Start time offset in seconds before the event time.
    end_offset: int = 150, # End time offset in seconds after the event time.
    output_format: str = "MSEED", # Output format for the waveforms. Can be 'MSEED', 'SAC', or 'WAV'.
    node: str = "NOA", # FDSN node to use for downloading waveforms. Available nodes can be found in obspy.clients.fdsn.header.URL_MAPPINGS.
    network_filter: List[str] = ["*"], # List of network codes to filter the stations. Default is all available networks ['*']. 
    threads: int = 1 # Number of threads to use for downloading waveforms. Default is 1.
):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    client = Client(node)

    if not Path(catalogue_path).exists():
        raise FileNotFoundError(f"Catalogue path does not exist: {catalogue_path}")

    valid_formats = ["MSEED", "SAC", "WAV"]
    if output_format not in valid_formats:
        raise ValueError(f"Invalid output format: {output_format}")

    if node not in sorted(URL_MAPPINGS.keys()):
        raise ValueError(f"Invalid node: {node}")

    logging.info(f"Reading seismic events from catalogue: {catalogue_path}")

    if str(catalogue_path).endswith(".xml"):
        evs = read_events(str(catalogue_path))
        events = [e.preferred_origin().time for e in evs]
        lat_list = [e.preferred_origin().latitude for e in evs]
        lon_list = [e.preferred_origin().longitude for e in evs]

    elif str(catalogue_path).endswith((".csv", ".txt", ".xls", ".xlsx")):
        if str(catalogue_path).endswith((".csv", ".txt")):
            df = pd.read_csv(catalogue_path, delimiter=detect_delimiter(catalogue_path))
        else:
            df = pd.read_excel(catalogue_path, engine='openpyxl')

        required_columns = ["Origin Time (GMT)", "Latitude", "Longitude"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        df["Origin Time (GMT)"] = pd.to_datetime(df["Origin Time (GMT)"])
        df["Origin Time (GMT)"] = df["Origin Time (GMT)"].apply(lambda x: UTCDateTime(x))
        events = df["Origin Time (GMT)"].tolist()
        lat_list = df["Latitude"].tolist()
        lon_list = df["Longitude"].tolist()
    else:
        raise ValueError("Unsupported catalogue format.")

    path_dict = make_event_folders(events, destination)

    logging.info(f'Number of seismic events: {len(events)}')
    logging.info(f'Station list: {station_list if station_list else "Dynamic based on bounding box or radius"}')
    
    
    for i, event in enumerate(events):
        logging.info(f"Processing event {i}/{len(events)}: {event}")
        print(f"station_list: {station_list} (type: {type(station_list)})")
        print(f"radius: {radius} (type: {type(radius)})")
        print(f"bbox: {bbox} (type: {type(bbox)})")

        if bbox is not None and all(b is None for b in bbox):
            bbox = None

        if station_list is not None and radius is None and bbox is None:
            station_codes = station_list if isinstance(station_list, list) else [station_list]
        
        elif station_list is None and radius is not None and bbox is None:
            print(f"Using radius: {radius} km")
            if not isinstance(radius, (int, float)) or radius <= 0:
                raise ValueError("Radius must be a positive number in kilometers.")
            try:
                station_codes = [] # Initialize an empty list to collect station codes
                for net in network_filter:
                    print(f"Fetching stations for network: {net}")
                    inv = client.get_stations(
                        network= f'{net}', latitude=lat_list[i], longitude=lon_list[i],
                        maxradius=kilometer2degrees(radius),  # Convert km to degrees
                        level='station', starttime=event - 600, endtime=event + 600
                    )
                    print(inv)
                    codes = get_inventory_stations(inv)  # Extract station codes
                    station_codes.extend(codes)
                    if not station_codes:
                        logging.warning(f"No stations found within {radius} km of event at {event}.")
                        continue
                station_codes = sorted(set(station_codes))  # Remove duplicates and sort
                logging.info(f"Found {len(station_codes)} stations within {radius} km of event at {event}.")
                logging.info(f"Station codes: {station_codes}")
            except Exception as e:
                logging.warning(f"Failed to retrieve stations: {e}")
                continue
        
        elif station_list is None and radius is None and bbox is not None:
            print(f"Using bounding box: {bbox}")
            if len(bbox) != 4:
                raise ValueError("Bounding box must be a list of four floats: [min_lat, max_lat, min_lon, max_lon].")
            try:
                station_codes = []  # Initialize an empty list to collect station codes
                for net in network_filter:
                    print(f"Fetching stations for network: {net}")
                    inv = client.get_stations(
                        network=f'{net}', minlatitude=bbox[0], maxlatitude=bbox[1],
                        minlongitude=bbox[2], maxlongitude=bbox[3],
                        level='station', starttime=event -1, endtime=event + 1
                    )
                    print(inv)
                    codes = get_inventory_stations(inv)
                    station_codes.extend(codes) # Collect all station codes
                    if not station_codes:
                        logging.warning(f"No stations found within bounding box {bbox} for event at {event}.")
                        continue
                
                station_codes = sorted(set(station_codes))  # Remove duplicates and sort
                logging.info(f"Found {len(station_codes)} stations within bounding box {bbox} for event at {event}.")
                logging.info(f"Station codes: {station_codes}")

            except Exception as e:
                logging.warning(f"Failed to retrieve stations: {e}")
                continue
       
        else:
            raise ValueError("Either provide a station list or specify a radius or bounding box, but not both.")

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {
                executor.submit(
                    fetch_waveform_for_station,
                    client,
                    code, 
                    event, 
                    start_offset, 
                    end_offset, 
                    channels
                ): code for code in station_codes
            }
            
            for future in as_completed(futures):
                code = futures[future]
                wf = future.result()
                
                try:
                   net, sta = code.split(".")[:2]  # Split the code into network and station
                   
                   if wf:
                        out_file = path_dict[str(event)] / f"{event.strftime('%Y%m%dT%H%M%S')}_{net}_{sta}.{output_format.lower()}"
                        write_waveform(wf, out_file, output_format)
                        logging.info(f"Waveform saved to {out_file}")
                
                except Exception as e:
                    logging.warning(f"Failed to write waveform for {code} at {event}: {e}")
            
