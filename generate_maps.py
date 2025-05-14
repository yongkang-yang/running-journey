#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import os

def generate_map_image(track_points, output_path, line_color='white', bg_color='black'):
    if not track_points:
        print(f"No track points for {output_path}, skipping image generation.")
        return

    lats = [p[0] for p in track_points]
    lons = [p[1] for p in track_points]

    if not lats or not lons:
        print(f"Empty latitudes or longitudes for {output_path}, skipping image generation.")
        return

    fig, ax = plt.subplots(figsize=(5, 5), dpi=100) # Keep DPI reasonable for web
    ax.plot(lons, lats, color=line_color, linewidth=1.5)
    
    # Make background transparent, lines will be white
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    ax.axis('off') # No axes, ticks, labels, or border
    ax.set_aspect('equal', adjustable='box') # Ensure aspect ratio is correct
    
    # Fit plot to data bounds tightly
    ax.set_xlim(min(lons), max(lons))
    ax.set_ylim(min(lats), max(lats))
    plt.margins(0.01) # Minimal margin

    plt.savefig(output_path, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)
    # print(f"Saved map image to {output_path}")

if __name__ == "__main__":
    data_file = "/home/ubuntu/running_website/processed_gpx_data.json"
    output_dir = "/home/ubuntu/running_website/map_images"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(data_file, 'r') as f:
        all_runs_data = json.load(f)

    image_count = 0
    for run_data in all_runs_data:
        filename_base = os.path.splitext(run_data["filename"])[0]
        output_image_path = os.path.join(output_dir, f"{filename_base}.png")
        
        # Assuming the first track contains the main route points
        # And track_points is a list of (lat, lon, ele) tuples
        if run_data["tracks"] and run_data["tracks"][0]:
            # The structure from process_gpx.py is run_data["tracks"] = [[(lat, lon, ele), ...]]
            # So we need run_data["tracks"][0] to get the list of points for the first track
            points_for_map = run_data["tracks"][0] 
            generate_map_image(points_for_map, output_image_path, line_color='white')
            image_count += 1
        else:
            print(f"No track data found for {run_data['filename']}")

    print(f"Generated {image_count} map images in {output_dir}")

