#!/usr/bin/env python3
import pandas as pd # type: ignore
from datetime import datetime

# Define the input and output file paths
input_file = "raw_data.csv"
output_file = "relevant_data.csv"

# Define the columns we want to keep
columns_to_keep = [
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "pickup_datetime",
    "dropoff_datetime"
]

# Print status update
print(f"Reading from {input_file}...")

# Use pandas to efficiently read the CSV, selecting only the columns we need
# This reduces memory usage since we're not loading unnecessary columns
df = pd.read_csv(input_file, usecols=columns_to_keep)

# Print status update
print(f"Extracted {len(df)} rows with {len(columns_to_keep)} columns")

# Process the datetime columns to remove date and convert to 24-hour format
print("Processing datetime columns...")

# Convert datetime columns to pandas datetime type for easier manipulation
# The format matches "08/15/2015 06:41:46 PM"
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], format='%m/%d/%Y %I:%M:%S %p')
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], format='%m/%d/%Y %I:%M:%S %p')

# Extract only the time part and format it as 24-hour time
df['pickup_datetime'] = df['pickup_datetime'].dt.strftime('%H:%M:%S')
df['dropoff_datetime'] = df['dropoff_datetime'].dt.strftime('%H:%M:%S')

print(f"Writing to {output_file}...")

# Write the dataframe to a new CSV file
df.to_csv(output_file, index=False)

# Print completion message
print(f"Done! Created {output_file} with the following columns:")
for col in columns_to_keep:
    print(f"- {col}")
print("\nDatetime columns now contain only 24-hour time format (HH:MM:SS)") 