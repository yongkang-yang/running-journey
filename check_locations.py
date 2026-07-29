#!/usr/bin/env python3
import gpxpy
import os
from collections import defaultdict
from pathlib import Path

# Function to get approximate location from first point
def get_location_from_gpx(filepath):
    try:
        with open(filepath, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            for track in gpx.tracks:
                for segment in track.segments:
                    if segment.points:
                        first_point = segment.points[0]
                        return (first_point.latitude, first_point.longitude)
        return None
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

# Approximate city boundaries (lat, lon ranges)
city_ranges = {
    "Rotterdam": {"lat": (51.85, 51.97), "lon": (4.40, 4.60)},
    "Copenhagen": {"lat": (55.60, 55.75), "lon": (12.45, 12.65)},
    "Berlin": {"lat": (52.40, 52.60), "lon": (13.25, 13.55)},
    "Chicago": {"lat": (41.70, 42.05), "lon": (-87.95, -87.50)},
}

def identify_city(lat, lon):
    for city, ranges in city_ranges.items():
        if (ranges["lat"][0] <= lat <= ranges["lat"][1] and 
            ranges["lon"][0] <= lon <= ranges["lon"][1]):
            return city
    return "Unknown"

# Check all new 2025-2026 files
new_files = [
    '2025-05-18_14515203014_Morning Run.gpx',
    '2025-05-26_14601788504_Evening Run.gpx',
    '2025-05-31_14648458665_Morning Run.gpx',
    '2025-06-02_14669116154_Morning Run.gpx',
    '2025-06-08_14730448418_Morning Run.gpx',
    '2025-06-25_14912720289_Afternoon Run.gpx',
    '2025-06-29_14949216016_Morning Run.gpx',
    '2025-07-03_14997357330_Evening Run.gpx',
    '2025-07-08_15047824402_Evening Run.gpx',
    '2025-07-10_15069933852_Evening Run.gpx',
    '2025-07-10_15072207593_Outdoor run.gpx',
    '2025-07-13_15096720069_Outdoor run.gpx',
    '2025-07-15_15125740612_Outdoor run.gpx',
    '2025-07-25_15228774519_Outdoor run in Copenhagen!.gpx',
    '2025-07-26_15238708975_Outdoor run.gpx',
    '2025-08-01_15310879646_Outdoor run.gpx',
    '2025-08-03_15326882817_Outdoor run.gpx',
    '2025-08-08_15390344941_Outdoor run.gpx',
    '2025-08-14_15459980454_Outdoor run.gpx',
    '2025-08-20_15528517224_Outdoor run.gpx',
    '2025-08-29_15623164642_Outdoor run.gpx',
    '2025-09-02_15674676522_Outdoor run.gpx',
    '2025-10-07_16063832433_Afternoon Run.gpx',
    '2025-10-20_16204864697_Afternoon Run.gpx',
    '2025-10-30_16309122401_Afternoon Run.gpx',
    '2025-11-06_16381118778_Evening Run.gpx',
    '2025-11-13_16447755969_Evening Run.gpx',
    '2025-11-20_16517721170_Evening Run.gpx',
    '2025-11-24_16554882186_Evening Run.gpx',
    '2025-11-25_16563721148_Evening Run.gpx',
    '2025-11-27_16585420530_Evening Run.gpx',
    '2025-11-29_16597890158_Morning Run.gpx',
    '2025-12-02_16632620450_Night Run.gpx',
    '2025-12-04_16650818064_Evening Run.gpx',
    '2025-12-06_16663479760_Morning Run.gpx',
    '2025-12-08_16687666424_Night Run.gpx',
    '2025-12-10_16708012710_Night Run.gpx',
    '2025-12-11_16716116642_Evening Run.gpx',
    '2025-12-14_16742635465_Evening Run.gpx',
    '2025-12-18_16776802673_Afternoon Run.gpx',
    '2025-12-22_16808899355_Morning Run.gpx',
    '2025-12-31_16892011146_Morning Run to 2026.gpx',
    '2026-01-04_16932935980_Lunch Run in the Snow.gpx',
    '2026-01-06_16957252920_Afternoon Run.gpx',
    '2026-01-08_16979785952_Afternoon Run.gpx',
    '2026-01-10_16999317690_Lunch Run.gpx',
]

gpx_dir = os.environ.get(
    "RUNNING_DATA_DIR",
    str(Path(__file__).resolve().parent / "gpx_data_private"),
)
location_groups = defaultdict(list)

for filename in new_files:
    filepath = os.path.join(gpx_dir, filename)
    if os.path.exists(filepath):
        coords = get_location_from_gpx(filepath)
        if coords:
            city = identify_city(coords[0], coords[1])
            location_groups[city].append({
                'filename': filename,
                'lat': coords[0],
                'lon': coords[1]
            })

# Print results
print("Location Analysis of New Activities:\n")
for city, activities in sorted(location_groups.items()):
    print(f"{city}: {len(activities)} activities")
    for activity in activities[:3]:  # Show first 3 as examples
        print(f"  - {activity['filename']} ({activity['lat']:.5f}, {activity['lon']:.5f})")
    if len(activities) > 3:
        print(f"  ... and {len(activities) - 3} more")
    print()
