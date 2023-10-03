import glob
import csv
import os
import folium

# Create a map object with custom settings
m = folium.Map(location=[43.041169, 12.560277], zoom_start=12)

# Define colors for each vehicle type
vehicle_colors = {
    "car": 'red',
    "bike": 'blue',
    "walk": '#00FF00',
    "train": 'magenta'
}

# Iterate over user folders
for user_folder in glob.glob('dataset/*'):
    user_id = os.path.basename(user_folder)  # Extract user ID from folder name

    # Iterate over the vehicle types (car, bike, walk, train)
    for vehicle_type in ["car", "bike", "walk", "train"]:
        # Iterate over the CSV files in the subfolder
        for file_path in glob.glob(f'{user_folder}/{vehicle_type}/signal-*.csv'):
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

                # Get the color based on the vehicle type
                color = vehicle_colors.get(vehicle_type, 'gray')  # Default to gray if type is unknown

                # Create the tooltip text
                tooltip = f'{user_id} - {vehicle_type} - {formatted_date}'

                # Iterate over the rows and extract latitudes and longitudes
                for row in reader:
                    latitude, longitude = float(row[0]), float(row[1])
                    # folium.CircleMarker(
                    #     location=[latitude, longitude],
                    #     radius=1,
                    #     color=color,
                    #     tooltip=tooltip,
                    #     weight=1,
                    #     fill_opacity=0.6,
                    #     opacity=1,
                    # ).add_to(m)

                    trail_coordinates.append((latitude, longitude))

                # # Add a polyline to the map with the trail coordinates, color, and tooltip
                folium.PolyLine(trail_coordinates, color=color, tooltip=tooltip).add_to(m)


# Save the map to an HTML file
m.save('map.html')
