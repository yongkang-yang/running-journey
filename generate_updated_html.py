#!/usr/bin/env python3
import json
import os

PROCESSED_DATA_FILE = "/home/ubuntu/updated_running_website/processed_gpx_data_with_locations.json"
STATS_FILE = "/home/ubuntu/updated_running_website/overall_running_stats_updated.json"
HTML_OUTPUT_FILE = "/home/ubuntu/updated_running_website/index.html"
MAP_IMAGE_DIR_RELATIVE = "updated_map_images" # Relative to index.html

def generate_html_content(runs_data, stats_data):
    html_parts = []

    # Header
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang=\"en\">")
    html_parts.append("<head>")
    html_parts.append("    <meta charset=\"UTF-8\">")
    html_parts.append("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
    html_parts.append("    <title>Johan\\'s Running Journey</title>")
    html_parts.append("    <link rel=\"stylesheet\" href=\"style.css\">")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append("    <div class=\"container\">")
    html_parts.append("        <header class=\"main-header\">")
    html_parts.append("            <h1>Run & Ride</h1>")
    html_parts.append("        </header>")

    # Group runs by city and country
    grouped_runs = {}
    for run in runs_data:
        city_country = f"{run.get('city', 'Unknown City')}, {run.get('country', 'Unknown Country')}"
        if city_country not in grouped_runs:
            grouped_runs[city_country] = []
        grouped_runs[city_country].append(run)
    
    # Sort city groups alphabetically by city_country key
    sorted_city_groups = sorted(grouped_runs.items())

    for city_country, runs_in_group in sorted_city_groups:
        html_parts.append(f"        <div class=\"city-group\">")
        html_parts.append(f"            <h2 class=\"city-group-header\">{city_country}</h2>")
        html_parts.append("            <div class=\"map-grid\">")
        for run in runs_in_group: # Runs are already sorted by filename within the group by the processing script
            img_filename = os.path.splitext(run["filename"])[0] + ".png"
            img_path = os.path.join(MAP_IMAGE_DIR_RELATIVE, img_filename)
            html_parts.append(f"                <img src=\"{img_path}\" alt=\"Run map for {run['filename']}\">")
        html_parts.append("            </div>") # Close map-grid
        html_parts.append("        </div>") # Close city-group

    # Statistics Section
    html_parts.append("        <div class=\"stats-section\">")
    html_parts.append("            <div class=\"overall-stats\">")
    html_parts.append("                <h2>STATISTICS</h2>")
    html_parts.append(f"                <p>Total Runs: {stats_data.get('total_runs', 0)}</p>")
    html_parts.append(f"                <p>Total Distance: {stats_data.get('total_distance_km', 0):.2f} km</p>")
    html_parts.append(f"                <p>Average Distance: {stats_data.get('average_distance_km_per_run', 0):.2f} km</p>")
    html_parts.append(f"                <p>Max Distance: {stats_data.get('max_distance_km_single_run', 0):.2f} km</p>")
    html_parts.append(f"                <p>Total Elevation Gain: {stats_data.get('total_elevation_gain_m', 0):.1f} m</p>")
    html_parts.append("            </div>") # Close overall-stats

    # Best Efforts Section (remains static as per user instructions)
    html_parts.append("            <div class=\"best-efforts\">")
    html_parts.append("                <h2>BEST EFFORTS</h2>")
    html_parts.append("                <p>400m: 1:05</p>")
    html_parts.append("                <p>1/2 mile: 3:04</p>")
    html_parts.append("                <p>1K: 3:58</p>")
    html_parts.append("                <p>1 mile: 6:42</p>")
    html_parts.append("                <p>2 mile: 13:00</p>")
    html_parts.append("                <p>5K: 22:30</p>")
    html_parts.append("                <p>10K: 46:17</p>")
    html_parts.append("                <p>15K: 1:13:23</p>")
    html_parts.append("                <p>10 mile: 1:18:57</p>")
    html_parts.append("                <p>20K: 1:38:30</p>")
    html_parts.append("                <p>Half-Marathon: 1:43:43</p>")
    html_parts.append("            </div>") # Close best-efforts
    html_parts.append("        </div>") # Close stats-section

    # Footer
    html_parts.append("        <footer>")
    html_parts.append("            <p class=\"footer-year\">YEAR</p>") # Placeholder
    html_parts.append("            <p class=\"footer-athlete\">ATHLETE</p>") # Placeholder
    html_parts.append("            <p class=\"footer-title\">Johan\\'s Running Journey</p>")
    html_parts.append("        </footer>")
    html_parts.append("    </div>") # Close container
    html_parts.append("</body>")
    html_parts.append("</html>")

    return "\n".join(html_parts)

if __name__ == "__main__":
    print(f"Reading processed data from: {PROCESSED_DATA_FILE}")
    try:
        with open(PROCESSED_DATA_FILE, "r", encoding="utf-8") as f:
            runs_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Processed data file not found at {PROCESSED_DATA_FILE}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {PROCESSED_DATA_FILE}: {e}")
        exit(1)

    print(f"Reading stats data from: {STATS_FILE}")
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            stats_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Stats file not found at {STATS_FILE}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {STATS_FILE}: {e}")
        exit(1)

    print("Generating new HTML content...")
    html_content = generate_html_content(runs_data, stats_data)

    print(f"Writing updated HTML to: {HTML_OUTPUT_FILE}")
    with open(HTML_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Successfully updated index.html.")

