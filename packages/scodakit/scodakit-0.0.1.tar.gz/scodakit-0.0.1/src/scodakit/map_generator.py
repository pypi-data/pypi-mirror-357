# -*- coding: utf-8 -*-
"""
map_generator.py

This script reads a catalogue of seismic events and their corresponding stations,
and generates a map visualizing the events and stations. It also exports the data in
various formats (GeoJSON, CSV, Shapefile).
"""
from pathlib import Path
import logging

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.img_tiles import GoogleTiles

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def load_data(catalogue_path):
    catalogue = pd.read_excel(catalogue_path)

    # Check required columns
    required = ["Latitude", "Longitude", "Magnitude (ML)", "Depth (km)", "Station_Latitude", "Station_Longitude", "Station"]
    for col in required:
        if col not in catalogue.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert to GeoDataFrames and ensure they have the same index
    catalogue = catalogue.dropna(subset=["Latitude", "Longitude", "Station_Latitude", "Station_Longitude"])
    if catalogue.empty:
        raise ValueError("Catalogue is empty after dropping rows with missing coordinates.")
    logging.info(f"Loaded catalogue with {len(catalogue)} events and {len(catalogue['Station'].unique())} unique stations.")
    # Create GeoDataFrames for events and stations
    # Ensure that the coordinates are in the correct format
    if not all(catalogue[["Latitude", "Longitude", "Station_Latitude", "Station_Longitude"]].apply(pd.to_numeric, errors='coerce').notnull().all()):
        raise ValueError("Coordinates must be numeric.")
    station_cat = catalogue.drop_duplicates(subset=["Station", "Station_Latitude", "Station_Longitude"])
    if station_cat.empty:
        raise ValueError("No unique stations found in the catalogue.")
    # Create GeoDataFrames
    logging.info("Creating GeoDataFrames for events and stations.")
    events_gdf = gpd.GeoDataFrame(
        catalogue,
        geometry=gpd.points_from_xy(catalogue["Longitude"], catalogue["Latitude"]),
        crs="EPSG:4326"
    )
    
    stations_gdf = gpd.GeoDataFrame(
        station_cat,
        geometry=gpd.points_from_xy(station_cat["Station_Longitude"], station_cat["Station_Latitude"]),
        crs="EPSG:4326"
    )

    return events_gdf, stations_gdf

def plot_map(events_gdf, stations_gdf, output_dir, image_formats):
    # Add tiles and features
    tiles = GoogleTiles(style="satellite")
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.add_image(tiles, 10, interpolation='bilinear')
    ax.set_title("Earthquake Epicentres and Stations")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    gl = ax.gridlines(draw_labels=True, linewidth=2.0, color='gray', alpha=0.5, linestyle='--') 
    gl.top_labels = False
    gl.right_labels = False
 
    stations_gdf.plot(ax=ax, marker="^", color="magenta", markersize=100, label="Stations", edgecolor="black", zorder=5)
    events_gdf.plot(ax=ax, marker="*", column ="Magnitude (ML)", cmap ='YlOrRd', alpha=1, legend=False, label="Seismic Epicentres", zorder=4, markersize=events_gdf["Magnitude (ML)"] ** 4)

    # add a label to the colour bar
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=events_gdf["Magnitude (ML)"].min(), vmax=events_gdf["Magnitude (ML)"].max()), cmap= 'YlOrRd')
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label("Magnitude (ML)", rotation=270, labelpad=30)
    

    # Add labels for stations
    for _, row in stations_gdf.iterrows():
        ax.text(row.geometry.x + 0.01, row.geometry.y + 0.01, row["Station"], fontsize=10, color="magenta")

    ax.legend()
    for fmt in image_formats:
        out_path = Path(output_dir) / f"seismic_map.{fmt}"
        plt.savefig(out_path, dpi=300)
        logging.info(f"Saved map to {out_path}")
    plt.close()


def export_data(events_gdf, stations_gdf, output_dir, formats):
    for fmt in formats:
        if fmt == "geojson":
            events_gdf.to_file(Path(output_dir) / "events.geojson", driver="GeoJSON")
            stations_gdf.to_file(Path(output_dir) / "stations.geojson", driver="GeoJSON")
        elif fmt == "csv":
            events_gdf.drop(columns="geometry").to_csv(Path(output_dir) / "events.csv", index=False)
            stations_gdf.drop(columns="geometry").to_csv(Path(output_dir) / "stations.csv", index=False)
        elif fmt == "shp":
            events_gdf.to_file(Path(output_dir) / "events.shp", driver="ESRI Shapefile")
            stations_gdf.to_file(Path(output_dir) / "stations.shp", driver="ESRI Shapefile")
        logging.info(f"Exported GIS data as {fmt}")


def generate_map(catalogue_path, output_dir, image_formats, export_formats):
    
    # Create output directory if it doesn't exist
    if not Path(output_dir).exists():
        logging.info(f"Creating output directory: {output_dir}")
    else:
        logging.info(f"Output directory already exists: {output_dir}")
    
    # Create the directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    events_gdf, stations_gdf = load_data(catalogue_path)
    plot_map(events_gdf, stations_gdf, output_dir, image_formats)
    export_data(events_gdf, stations_gdf, output_dir, export_formats)
