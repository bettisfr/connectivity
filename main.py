import glob
import csv
import os
import folium

# Create a map object with custom settings
m = folium.Map(location=[43.041169, 12.560277], zoom_start=12)

# Iterate over the "bike" and "car" folders
for folder_name in ["bike", "car"]:
    # Iterate over the CSV files in the subfolder
    for file_path in glob.glob(f'dataset/{folder_name}/signal-*.csv'):
        # Extract the date from the file name
        file_name = os.path.basename(file_path)
        date = file_name.split('-')[1:]
        formatted_date = '-'.join(date).split('.')[0]

        # Read the CSV file
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row if it exists

            # Create a list to store the trail coordinates
            trail_coordinates = []

            # Iterate over the rows and extract latitudes and longitudes
            for row in reader:
                latitude, longitude = float(row[0]), float(row[1])
                trail_coordinates.append((latitude, longitude))

            # Determine the color based on the folder name
            color = 'blue' if folder_name == 'bike' else 'red'

            # Create the tooltip text
            tooltip = f'{folder_name} {formatted_date}'

            # Add a polyline to the map with the trail coordinates, color, and tooltip
            folium.PolyLine(trail_coordinates, color=color, tooltip=tooltip).add_to(m)

# Save the map to an HTML file
m.save('map.html')
