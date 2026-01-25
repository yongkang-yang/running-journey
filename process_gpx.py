#!/usr/bin/env python3
import os
import gpxpy
import gpxpy.gpx
import json
from math import radians, sin, cos, sqrt, atan2
import xml.etree.ElementTree as ET

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance between two lat/lon points
    R = 6371  # Radius of Earth in kilometers
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat / 2)**2 + cos(lat1) * cos(lat2) * sin(dLon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance # in km

def parse_tcx_file(filepath):
    """Parse TCX file and convert to GPX-like structure"""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # TCX namespace
    ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    tracks = []
    for activity in root.findall('.//tcx:Activity', ns):
        for lap in activity.findall('.//tcx:Lap', ns):
            track_points = []
            for trackpoint in lap.findall('.//tcx:Trackpoint', ns):
                position = trackpoint.find('.//tcx:Position', ns)
                if position is not None:
                    lat_elem = position.find('tcx:LatitudeDegrees', ns)
                    lon_elem = position.find('tcx:LongitudeDegrees', ns)
                    alt_elem = trackpoint.find('tcx:AltitudeMeters', ns)
                    
                    if lat_elem is not None and lon_elem is not None:
                        lat = float(lat_elem.text)
                        lon = float(lon_elem.text)
                        alt = float(alt_elem.text) if alt_elem is not None and alt_elem.text else None
                        track_points.append((lat, lon, alt))
            if track_points:
                tracks.append(track_points)
    return tracks

def process_gpx_files(gpx_dir):
    all_runs_data = []
    total_distance_all_runs = 0
    total_elevation_gain_all_runs = 0
    max_distance_single_run = 0
    run_count = 0
    corrupted_files = []

    for filename in os.listdir(gpx_dir):
        if filename.endswith(".gpx") or filename.endswith(".tcx"):
            filepath = os.path.join(gpx_dir, filename)
            try:
                run_data = {
                    "filename": filename,
                    "tracks": []
                }
                run_total_distance = 0
                run_total_elevation_gain = 0
                
                if filename.endswith(".gpx"):
                    with open(filepath, 'r') as gpx_file:
                        gpx = gpxpy.parse(gpx_file)
                    
                    for track in gpx.tracks:
                        track_points = []
                        previous_point = None
                        for segment in track.segments:
                            for point_idx, point in enumerate(segment.points):
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
                else:  # TCX file
                    tracks = parse_tcx_file(filepath)
                    for track_points in tracks:
                        previous_point = None
                        for point in track_points:
                            if previous_point:
                                segment_distance = calculate_distance(previous_point[0], previous_point[1], point[0], point[1])
                                run_total_distance += segment_distance
                                if point[2] is not None and previous_point[2] is not None:
                                    elevation_diff = point[2] - previous_point[2]
                                    if elevation_diff > 0:
                                        run_total_elevation_gain += elevation_diff
                            previous_point = point
                        run_data["tracks"].append(track_points)
                
                run_data["distance_km"] = run_total_distance
                run_data["elevation_gain_m"] = run_total_elevation_gain
                all_runs_data.append(run_data)

                total_distance_all_runs += run_total_distance
                total_elevation_gain_all_runs += run_total_elevation_gain
                if run_total_distance > max_distance_single_run:
                    max_distance_single_run = run_total_distance
                run_count += 1
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
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

if __name__ == "__main__":
    gpx_directory = "/Users/johanyang/Github Repo/running-journey/gpx_data"
    output_data_file = "/Users/johanyang/Github Repo/running-journey/processed_gpx_data.json"
    output_stats_file = "/Users/johanyang/Github Repo/running-journey/overall_running_stats.json"

    runs_data, stats_data = process_gpx_files(gpx_directory)

    with open(output_data_file, 'w') as f_data:
        json.dump(runs_data, f_data, indent=4)
    
    with open(output_stats_file, 'w') as f_stats:
        json.dump(stats_data, f_stats, indent=4)

    print(f"Processed {stats_data['total_runs']} GPX/TCX files.")
    print(f"Individual run data saved to {output_data_file}")
    print(f"Overall statistics saved to {output_stats_file}")
    if stats_data['corrupted_files']:
        print(f"Corrupted files: {stats_data['corrupted_files']}")

