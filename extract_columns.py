#!/usr/bin/env python3
import pandas as pd # type: ignore
from datetime import datetime
import random
import string

# Define the input and output file paths
input_file = "Raw Data.csv"
output_file = "relevantdata.csv"

# Define the columns we want to keep
columns_to_keep = [
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "pickup_datetime"
]

# Print status update
print(f"Reading from {input_file}...")

# Use pandas to efficiently read the CSV, selecting only the columns we need
# This reduces memory usage since we're not loading unnecessary columns
df = pd.read_csv(input_file, usecols=columns_to_keep)

# Print status update
print(f"Extracted {len(df)} rows with {len(columns_to_keep)} columns")

# Process the pickup_datetime column to remove date and convert to 24-hour format
print("Processing pickup_datetime column...")

# Convert pickup_datetime to pandas datetime type for easier manipulation
# The format matches "08/15/2015 06:41:46 PM"
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], format='%m/%d/%Y %I:%M:%S %p')

# Extract only the time part and format it as 24-hour time
df['pickup_datetime'] = df['pickup_datetime'].dt.strftime('%H:%M:%S')

# Generate unique 6-letter uppercase IDs for each row
print("Generating unique trip IDs...")

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

# Generate the IDs and add as the first column
unique_ids = generate_unique_ids(len(df))
df.insert(0, 'trip_id', unique_ids)

print(f"Writing to {output_file}...")

# Write the dataframe with the new IDs to a new CSV file
df.to_csv(output_file, index=False)

# Print completion message
print(f"Done! Created {output_file} with the following columns:")
print(f"- trip_id (new unique 6-letter ID)")
for col in columns_to_keep:
    print(f"- {col}")
print("\nPickup_datetime column now contains only 24-hour time format (HH:MM:SS)") 