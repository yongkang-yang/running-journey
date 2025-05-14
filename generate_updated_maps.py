#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import os

# --- Constants ---
DATA_FILE = "/home/ubuntu/updated_running_website/processed_gpx_data_with_locations.json"
OUTPUT_DIR = "/home/ubuntu/updated_running_website/updated_map_images"
LINE_COLOR = "white"

# --- Helper Function for Map Generation ---
def generate_map_image_updated(track_points, output_path, line_color=LINE_COLOR, bg_color=None):
    if not track_points:
        # print(f"No track points for {output_path}, skipping image generation.")
        return

    lats = [p[0] for p in track_points]
    lons = [p[1] for p in track_points]

    if not lats or not lons or len(lats) < 2 or len(lons) < 2: # Need at least 2 points to draw a line
        # print(f"Insufficient points for {output_path}, skipping image generation.")
        return

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100) # Adjust figsize/dpi as needed for web
    
    # Plot the track
    ax.plot(lons, lats, color=line_color, linewidth=1.5)
    
    # Ensure transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Remove all axes, ticks, labels, and the plot frame/border
    ax.axis("off") 
    
    # Set aspect ratio to be equal, so the map is not distorted
    ax.set_aspect("equal", adjustable="box")
    
    # Fit plot to data bounds tightly, with minimal margin to avoid cutting off lines
    lon_min, lon_max = min(lons), max(lons)
    lat_min, lat_max = min(lats), max(lats)
    
    if lon_min == lon_max:
        lon_max += 0.0001 # Add a tiny offset
    if lat_min == lat_max:
        lat_max += 0.0001

    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0, transparent=True, dpi=fig.dpi)
    plt.close(fig)
    # print(f"Saved updated map image to {output_path}")

# --- Main Script Execution ---
if __name__ == "__main__":
    print(f"Input Data File: {DATA_FILE}")
    print(f"Output Directory for Maps: {OUTPUT_DIR}")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_runs_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at {DATA_FILE}. Exiting.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {DATA_FILE}. Exiting.")
        exit(1)

    image_count = 0
    total_runs = len(all_runs_data)
    print(f"Found {total_runs} runs in the data file.")

    for idx, run_data in enumerate(all_runs_data):
        filename_base = os.path.splitext(run_data["filename"])[0]
        output_image_path = os.path.join(OUTPUT_DIR, f"{filename_base}.png")
        
        # print(f"Processing run {idx+1}/{total_runs}: {run_data['filename']}") # Corrected here

        if run_data.get("tracks") and run_data["tracks"][0]:
            points_for_map = run_data["tracks"][0]
            generate_map_image_updated(points_for_map, output_image_path, line_color=LINE_COLOR)
            image_count += 1
        else:
            print(f"  -> No track data found or tracks are empty for {run_data['filename']}. Skipping map generation.") # Corrected here

    print(f"\nGenerated {image_count} updated map images in {OUTPUT_DIR}")

