import glob
import csv
import folium
import os

# Create base map
m = folium.Map(location=[43.041169, 12.560277], zoom_start=12)

# Bounding box coordinates
min_lon = 11.891377
max_lon = 13.262951
max_lat = 43.617910
min_lat = 42.362570

# Step 1: Extract cell_ids and process trails from both dataset/*.csv and dataset-old/* folders
observed_cell_ids = set()

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
                    # For dataset-old, the latitude is in the 1st column, longitude in the 2nd, and cell_id in the 7th
                    if folder.startswith('dataset-old'):
                        lat = float(row[0])
                        lon = float(row[1])
                        cell_id = int(row[6])
                    else:
                        lat = float(row["lat"])
                        lon = float(row["lon"])
                        cell_id = int(row["cell_id"])

                    # Add cell_id to observed_cell_ids
                    observed_cell_ids.add(cell_id)

                    # Add to trail coordinates
                    trail_coordinates.append((lat, lon))

                except (ValueError, IndexError, KeyError):
                    continue

            # If trail data exists, draw it on the map
            if trail_coordinates:
                trail_color = 'green' if folder.startswith('dataset-old') else 'blue'
                folium.PolyLine(trail_coordinates, color=trail_color, tooltip=formatted_date).add_to(m)

# Step 2: Read and filter towers from tim_lteitaly.clf file
tower_locations = []

with open('towers/tim_lteitaly.clf', 'r') as tower_file:
    for line in tower_file:
        parts = line.strip().split(';')  # Split by semicolon
        if len(parts) < 6:
            continue

        try:
            cell_id = int(parts[1])  # cell_id in the 2nd column
            lat = float(parts[4])  # latitude in the 5th column
            lon = float(parts[5])  # longitude in the 6th column
        except ValueError:
            continue

        # Only add tower if its cell_id is in observed_cell_ids
        if cell_id in observed_cell_ids:
            tower_locations.append((lat, lon, cell_id))

# Step 3: Add filtered towers with smaller markers
for lat, lon, cell_id in tower_locations:
    folium.CircleMarker(
        location=(lat, lon),
        radius=4,  # Smaller size
        color='red',
        fill=True,
        fill_opacity=0.8,
        popup=f"Cell ID: {cell_id}"
    ).add_to(m)

# Save the final map
m.save('map.html')
