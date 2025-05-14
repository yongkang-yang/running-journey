#!/usr/bin/env python3
import os
import gpxpy
import gpxpy.gpx
import json
import requests # For making HTTP requests to Nominatim
import time # For adding delays between API requests
from math import radians, sin, cos, sqrt, atan2

# --- Constants ---
GPX_DIR = "/home/ubuntu/updated_running_website/all_gpx_data"
OUTPUT_DATA_FILE = "/home/ubuntu/updated_running_website/processed_gpx_data_with_locations.json"
OUTPUT_STATS_FILE = "/home/ubuntu/updated_running_website/overall_running_stats_updated.json"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "JohanRunningWebsiteUpdater/1.0 (manus.ai agent; +https://manus.ai)"

# --- Helper Functions ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance  # in km

def get_location_from_coords(lat, lon):
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon,
        "zoom": 10 # City level
    }
    headers = {
        "User-Agent": USER_AGENT
    }
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        address = data.get("address", {})
        city = address.get("city", address.get("town", address.get("village", "Unknown City")))
        country = address.get("country", "Unknown Country")
        return city, country
    except requests.exceptions.RequestException as e:
        print(f"Nominatim API request failed: {e}")
        return "Unknown City", "Unknown Country"
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response from Nominatim.")
        return "Unknown City", "Unknown Country"
    finally:
        time.sleep(1.1) # Adhere to Nominatim's 1 req/sec policy

# --- Main Processing Function ---
def process_gpx_files_with_location(gpx_dir):
    all_runs_data = []
    total_distance_all_runs = 0
    total_elevation_gain_all_runs = 0
    max_distance_single_run = 0
    run_count = 0
    corrupted_files = []
    location_cache = {} # Simple cache for identical start points if any

    gpx_file_list = sorted([f for f in os.listdir(gpx_dir) if f.endswith(".gpx")])
    total_files = len(gpx_file_list)
    print(f"Starting processing of {total_files} GPX files...")

    for idx, filename in enumerate(gpx_file_list):
        print(f"Processing file {idx+1}/{total_files}: {filename}")
        filepath = os.path.join(gpx_dir, filename)
        city = "Unknown City"
        country = "Unknown Country"
        first_lat, first_lon = None, None

        try:
            with open(filepath, 'r', encoding='utf-8') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
            
            run_data = {
                "filename": filename,
                "tracks": [],
                "city": city,
                "country": country
            }
            run_total_distance = 0
            run_total_elevation_gain = 0
            
            first_point_found = False
            for track_idx, track in enumerate(gpx.tracks):
                track_points = []
                previous_point = None
                for segment_idx, segment in enumerate(track.segments):
                    for point_idx, point in enumerate(segment.points):
                        if not first_point_found:
                            first_lat, first_lon = point.latitude, point.longitude
                            first_point_found = True
                        
                        track_points.append((point.latitude, point.longitude, point.elevation))
                        if previous_point:
                            segment_distance = calculate_distance(previous_point.latitude, previous_point.longitude, point.latitude, point.longitude)
                            run_total_distance += segment_distance
                            if point.elevation and previous_point.elevation:
                                elevation_diff = point.elevation - previous_point.elevation
                                if elevation_diff > 0:
                                    run_total_elevation_gain += elevation_diff
                        previous_point = point
                run_data["tracks"].append(track_points)
            
            if first_lat is not None and first_lon is not None:
                cache_key = (round(first_lat, 4), round(first_lon, 4)) # Cache with some precision
                if cache_key in location_cache:
                    city, country = location_cache[cache_key]
                    print(f"  -> Using cached location for {filename}: {city}, {country}")
                else:
                    print(f"  -> Fetching location for {filename} ({first_lat}, {first_lon})...")
                    city, country = get_location_from_coords(first_lat, first_lon)
                    location_cache[cache_key] = (city, country)
                    print(f"  -> Location found: {city}, {country}")
            else:
                print(f"  -> No valid first point found in {filename} to determine location.")

            run_data["city"] = city
            run_data["country"] = country
            run_data["distance_km"] = run_total_distance
            run_data["elevation_gain_m"] = run_total_elevation_gain
            all_runs_data.append(run_data)

            total_distance_all_runs += run_total_distance
            total_elevation_gain_all_runs += run_total_elevation_gain
            if run_total_distance > max_distance_single_run:
                max_distance_single_run = run_total_distance
            run_count += 1
        except gpxpy.gpx.GPXXMLSyntaxException as e:
            print(f"GPX XML Syntax Error processing file {filename}: {e}")
            corrupted_files.append(filename)
        except Exception as e:
            print(f"Generic Error processing file {filename}: {e}")
            corrupted_files.append(filename)
    
    average_distance_per_run = total_distance_all_runs / run_count if run_count > 0 else 0

    overall_stats = {
        "total_runs": run_count,
        "total_distance_km": total_distance_all_runs,
        "average_distance_km_per_run": average_distance_per_run,
        "max_distance_km_single_run": max_distance_single_run,
        "total_elevation_gain_m": total_elevation_gain_all_runs,
        "corrupted_files": corrupted_files
    }

    return all_runs_data, overall_stats

# --- Script Execution ---
if __name__ == "__main__":
    print(f"GPX Directory: {GPX_DIR}")
    print(f"Output Data File: {OUTPUT_DATA_FILE}")
    print(f"Output Stats File: {OUTPUT_STATS_FILE}")

    runs_data, stats_data = process_gpx_files_with_location(GPX_DIR)

    # Sort data by city, then by filename (as a proxy for date if filenames are date-based)
    runs_data_sorted = sorted(runs_data, key=lambda x: (x.get('city', 'ZZZ'), x.get('country', 'ZZZ'), x['filename']))

    with open(OUTPUT_DATA_FILE, 'w', encoding='utf-8') as f_data:
        json.dump(runs_data_sorted, f_data, indent=4, ensure_ascii=False)
    
    with open(OUTPUT_STATS_FILE, 'w', encoding='utf-8') as f_stats:
        json.dump(stats_data, f_stats, indent=4, ensure_ascii=False)

    print(f"\nProcessed {stats_data['total_runs']} GPX files.")
    print(f"Individual run data with locations saved to {OUTPUT_DATA_FILE}")
    print(f"Overall statistics saved to {OUTPUT_STATS_FILE}")
    if stats_data['corrupted_files']:
        print(f"Corrupted files: {stats_data['corrupted_files']}")

