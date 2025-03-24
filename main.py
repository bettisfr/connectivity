import glob
import csv
import folium
import os

# Create a map object
m = folium.Map(location=[43.041169, 12.560277], zoom_start=12)

# Iterate over the CSV files in the dataset folder
for file_path in glob.glob('dataset/*.csv'):
    file_name = os.path.basename(file_path)  # Extract file name
    formatted_date = file_name.split('.')[0]  # Remove file extension

    # Read the CSV file
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        # Create a list to store the trail coordinates
        trail_coordinates = []

        # Iterate over the rows and extract latitudes and longitudes
        for row in reader:
            try:
                latitude = float(row["lat"])
                longitude = float(row["lon"])
                trail_coordinates.append((latitude, longitude))
            except ValueError:
                continue  # Skip invalid rows

        # Add a polyline to the map if there are valid coordinates
        if trail_coordinates:
            folium.PolyLine(trail_coordinates, color='blue', tooltip=formatted_date).add_to(m)

# Save the map to an HTML file
m.save('map.html')
