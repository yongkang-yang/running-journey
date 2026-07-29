#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt


REPOSITORY_ROOT = Path(__file__).resolve().parent


def default_data_file():
    configured_directory = os.environ.get("RUNNING_DERIVED_DIR")
    if configured_directory:
        return Path(configured_directory).expanduser() / "processed_gpx_data.json"

    configured_input = os.environ.get("RUNNING_DATA_DIR")
    input_directory = Path(configured_input).expanduser() if configured_input else REPOSITORY_ROOT / "gpx_data_private"
    return input_directory.resolve().parent / "derived" / "processed_gpx_data.json"

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

def main():
    parser = argparse.ArgumentParser(
        description="Generate public route-map images from private processed route data."
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=default_data_file(),
        help="Private processed route JSON (default: RUNNING_DERIVED_DIR or OneDrive derived directory).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPOSITORY_ROOT / "updated_map_images",
        help="Directory for public map images.",
    )
    args = parser.parse_args()

    data_file = args.data_file.expanduser()
    output_dir = args.output_dir.expanduser()
    if not data_file.is_file():
        parser.error(f"Processed route data does not exist: {data_file}")
    output_dir.mkdir(parents=True, exist_ok=True)

    with data_file.open("r", encoding="utf-8") as f:
        all_runs_data = json.load(f)

    image_count = 0
    for run_data in all_runs_data:
        filename_base = os.path.splitext(run_data["filename"])[0]
        output_image_path = output_dir / f"{filename_base}.png"

        if run_data["tracks"] and run_data["tracks"][0]:
            points_for_map = run_data["tracks"][0]
            generate_map_image(points_for_map, output_image_path, line_color='white')
            image_count += 1
        else:
            print(f"No track data found for {run_data['filename']}")

    print(f"Generated {image_count} map images in {output_dir}")


if __name__ == "__main__":
    main()
