# Yongkang's Running Journey

A visualization project that displays running activities from GPX and TCX files with maps grouped by location.

![image](https://github.com/user-attachments/assets/1bffed8a-eab4-4282-bdc4-ecb391d8cb02)


## Overview

This project creates a visually appealing website to showcase running activities tracked through various fitness apps. It processes GPX files from Strava and TCX files from Nike Run Club, extracts route data, generates map visualizations, and organizes them by location.

The website features:

- Clean, minimalist black and white design
- Route maps displayed as white lines on black background
- Activities grouped by city and country
- Overall statistics (total distance, elevation gain, etc.)
- Personal best efforts for various distances

## Technologies Used

- **HTML/CSS**: For the website structure and styling
- **Python**: For data processing and visualization
- **Libraries**:
  - `gpxpy`: For parsing GPX files
  - `matplotlib`: For generating route visualizations
  - `requests`: For reverse geocoding to identify locations

## Project Structure

```
Yongkang-running-journey/
├── index.html              # Main website HTML
├── style.css               # CSS styling
├── updated_map_images/     # Generated route visualizations
├── scripts/                # Data processing scripts
│   ├── process_gpx_files.py       # GPX file processor (included in repo)
│   ├── process_tcx_files.py       # TCX file processor
│   ├── generate_maps.py           # Map visualization generator
└── data/                   # Source data (included in repo)
```

## How It Works

1. **Data Processing**: The Python scripts parse GPX and TCX files to extract route coordinates, distance, elevation, and other metrics.

2. **Location Identification**: Using reverse geocoding, each run is assigned a city and country based on its starting coordinates.

3. **Map Generation**: For each activity, a map visualization is created showing the route as a white line on a black background.

4. **Website Generation**: The HTML is dynamically generated to group activities by location and display overall statistics.

## Private data workflow

Raw GPX, TCX, and COROS FIT exports are intentionally kept out of this repository. On the primary WSL machine they live in OneDrive at:

```
/mnt/c/Users/ykyan/OneDrive/Life_YONGKANG/WIKI-YANG/data/running-journey/raw-tracks
```

`gpx_data_private` is a local-only symlink to that directory. It is ignored by Git. To refresh the site after adding new exports, install the dependencies and run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python process_gpx.py
.venv/bin/python generate_maps.py
```

The first command writes complete route coordinates only to the adjacent OneDrive `derived/` folder. The second command writes public route-map images to `updated_map_images/`; review those images and update `index.html` before committing a deployment.


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Strava and Nike Run Club for providing activity export functionality
- OpenStreetMap for reverse geocoding data
- The running community @yihong0618 for [inspiration](https://github.com/yihong0618/running_page)

---

Created with ❤️ for runners.
