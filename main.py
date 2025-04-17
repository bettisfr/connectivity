import glob
import csv
import folium
import os
from scipy.spatial import ConvexHull
import numpy as np
import matplotlib.pyplot as plt

# Create base map
m = folium.Map(location=[43.041169, 12.560277], zoom_start=12)

# Step 1: Extract cell_ids and process trails from both dataset/*.csv and dataset-old/* folders
observed_cell_ids = set()

# Create a list of observations
observations = []

# Loop through both dataset and dataset-old folders
for folder in ['dataset', 'dataset-old/bike', 'dataset-old/car', 'dataset-old/train', 'dataset-old/walk']:
    for file_path in glob.glob(f'{folder}/*.csv'):
        file_name = os.path.basename(file_path)

        # Skip files that include 'ocid' in the name (for dataset/*.csv only)
        if 'ocid' in file_name and folder == 'dataset':
            continue

        formatted_date = file_name.split('.')[0]

        with open(file_path, 'r') as file:
            reader = csv.reader(file) if folder.startswith('dataset-old') else csv.DictReader(file)
            trail_coordinates = []

            # Loop through each row
            for row in reader:
                try:
                    if folder.startswith('dataset-old'):
                        lat = float(row[0])
                        lon = float(row[1])
                        alt = int(row[2])
                        cell_id = int(row[6])
                        signal = int(row[7])
                    else:
                        lat = float(row["lat"])
                        lon = float(row["lon"])
                        alt = int(float(row["altitude"]))
                        cell_id = int(row["cell_id"])
                        signal = int(row["rsrp"]) if row["net_type"] == "LTE" else int(row["rssi"])

                    # Add element to the observations list
                    observations.append({
                        "lat": lat,
                        "lon": lon,
                        "alt": alt,
                        "cell_id": cell_id,
                        "signal": signal
                    })

                    # Add cell_id to observed_cell_ids
                    observed_cell_ids.add(cell_id)

                    # Add to trail coordinates
                    trail_coordinates.append((lat, lon))

                except (ValueError, IndexError, KeyError):
                    continue

            folium.PolyLine(trail_coordinates, color='blue', tooltip=formatted_date).add_to(m)

# Step 2: Read and filter towers from tim_lteitaly.clf and vodafone_lteitaly.clf files
towers = []

# Loop through *.clf files
for tower_file in ['towers/tim_lteitaly.clf', 'towers/vodafone_lteitaly.clf']:
    with open(tower_file, 'r') as file:
        for line in file:
            parts = line.strip().split(';')
            if len(parts) < 6:
                continue

            try:
                cell_id = int(parts[1])
                lat = float(parts[4])
                lon = float(parts[5])
            except ValueError:
                continue

            # Only add tower if its cell_id is in observed_cell_ids
            if cell_id in observed_cell_ids:
                towers.append({
                    "lat": lat,
                    "lon": lon,
                    "cell_id": cell_id
                })

# Step 3: Add filtered towers with smaller markers
for tower in towers:
    lat = tower["lat"]
    lon = tower["lon"]
    cell_id = tower["cell_id"]

    folium.CircleMarker(
        location=(lat, lon),
        radius=4,
        color='red',
        fill=True,
        fill_opacity=0.8,
        popup=f"Cell ID: {cell_id}"
    ).add_to(m)

# Print all observations
print(f"Total observations: {len(observations)}")
print(f"Sample observation: {observations[0] if observations else 'None'}")

# Print all towers
print(f"Total filtered towers: {len(towers)}")
print(f"Sample tower: {towers[0] if towers else 'None'}")

# --- Test: Find and highlight the tower with the most matching observations and draw convex hull ---
if towers:
    best_tower = None
    max_matches = 0
    best_matching_obs = []

    for tower in towers:
        cell_id = tower["cell_id"]
        matching_obs = [obs for obs in observations if obs["cell_id"] == cell_id]

        if len(matching_obs) > max_matches:
            best_tower = tower
            max_matches = len(matching_obs)
            best_matching_obs = matching_obs

    if best_tower:
        print(f"\n[TEST] Best tower Cell ID: {best_tower['cell_id']} with {max_matches} matches")

        # Highlight the tower in magenta
        folium.CircleMarker(
            location=(best_tower["lat"], best_tower["lon"]),
            radius=8,
            color='magenta',
            fill=True,
            fill_opacity=1.0,
        ).add_to(m)

        # Get min and max signal values
        signal_values = [obs["signal"] for obs in best_matching_obs]
        min_signal = min(signal_values)
        max_signal = max(signal_values)

        # Normalize and convert to color
        for obs in best_matching_obs:
            norm_signal = (obs["signal"] - min_signal) / (max_signal - min_signal + 1e-6)  # avoid division by zero
            rgba = plt.cm.jet(norm_signal)  # use jet colormap
            hex_color = "#{:02x}{:02x}{:02x}".format(int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255))

            folium.CircleMarker(
                location=(obs["lat"], obs["lon"]),
                radius=5,
                color=hex_color,
                fill=True,
                fill_opacity=1.0,
                tooltip=f"Signal: {obs['signal']}"
            ).add_to(m)

        # Prepare points for convex hull: yellow + magenta
        points = [(obs["lat"], obs["lon"]) for obs in best_matching_obs]
        points.append((best_tower["lat"], best_tower["lon"]))  # include magenta tower

        if len(points) >= 3:
            # Convert to numpy array for ConvexHull
            np_points = np.array(points)
            hull = ConvexHull(np_points)

            hull_points = [tuple(np_points[i]) for i in hull.vertices]

            # Draw convex hull polygon
            folium.Polygon(
                locations=hull_points,
                color='black',
                weight=2,
                fill=True,
                fill_opacity=0.2
            ).add_to(m)
        else:
            print("[TEST] Not enough points to compute a convex hull.")
    else:
        print("[TEST] No tower with matching observations found.")
else:
    print("[TEST] No towers available to test.")


# Save the final map
m.save('map.html')
