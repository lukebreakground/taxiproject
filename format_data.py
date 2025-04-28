#!/usr/bin/env python3
import pandas as pd
from datetime import datetime
import random
import string

# Define the input and output file paths
input_file = "relevant_data.csv"
output_file = "formatted_data.csv"

def generate_unique_ids(num_ids, id_length=6):
    """
    Generate a list of unique random uppercase alphabetic IDs
    
    Args:
        num_ids: Number of IDs to generate
        id_length: Length of each ID (default 6)
        
    Returns:
        List of unique IDs
    """
    # Create a set to track used IDs for faster lookup
    used_ids = set()
    
    # List to store all generated IDs
    all_ids = []
    
    # Keep generating IDs until we have enough
    while len(all_ids) < num_ids:
        # Generate a random ID with uppercase letters
        new_id = ''.join(random.choices(string.ascii_uppercase, k=id_length))
        
        # Only add it if it's unique
        if new_id not in used_ids:
            used_ids.add(new_id)
            all_ids.append(new_id)
    
    return all_ids

def calculate_elapsed_time(pickup_time, dropoff_time):
    """
    Calculate elapsed time between pickup and dropoff times
    
    Args:
        pickup_time: Pickup time in format 'HH:MM:SS'
        dropoff_time: Dropoff time in format 'HH:MM:SS'
        
    Returns:
        Elapsed time in seconds
    """
    # Parse the time strings
    pickup_dt = datetime.strptime(pickup_time, '%H:%M:%S')
    dropoff_dt = datetime.strptime(dropoff_time, '%H:%M:%S')
    
    # Calculate time difference in seconds
    # If dropoff is earlier than pickup (crossing midnight), add a day
    if dropoff_dt < pickup_dt:
        # This assumes no trip is longer than 24 hours
        from datetime import timedelta
        dropoff_dt = dropoff_dt + timedelta(days=1)
    
    # Calculate the time difference in seconds
    time_diff = (dropoff_dt - pickup_dt).total_seconds()
    
    return time_diff

# Print status update
print(f"Reading from {input_file}...")

# Read the CSV file
df = pd.read_csv(input_file)

# Print status update
print(f"Processing {len(df)} rows...")

# Generate unique trip IDs
print("Generating unique trip IDs...")
unique_ids = generate_unique_ids(len(df))
df.insert(0, 'trip_id', unique_ids)

# Calculate elapsed time between pickup and dropoff
print("Calculating elapsed times...")
df['elapsed_time'] = df.apply(
    lambda row: calculate_elapsed_time(row['pickup_datetime'], row['dropoff_datetime']), 
    axis=1
)

# Remove the datetime columns since they're no longer needed
print("Removing datetime columns...")
df = df.drop(columns=['pickup_datetime', 'dropoff_datetime'])

print(f"Writing to {output_file}...")

# Write the dataframe to a new CSV file
df.to_csv(output_file, index=False)

# Print completion message
print(f"Done! Created {output_file} with the following columns:")
for col in df.columns:
    print(f"- {col}")
print("\nAdded new columns:")
print("- trip_id (unique 6-letter ID)")
print("- elapsed_time (trip duration in seconds)")
print("\nRemoved columns:")
print("- pickup_datetime")
print("- dropoff_datetime") 