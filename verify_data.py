#!/usr/bin/env python3
import pandas as pd
from datetime import datetime
import sys

def verify_data(raw_file, processed_file):
    """
    Verify that:
    1. No data was lost or modified during processing (except for datetime format)
    2. All trip IDs are unique
    
    Args:
        raw_file: Path to the original raw data CSV
        processed_file: Path to the processed data CSV with IDs
    """
    print(f"Reading raw data from {raw_file}...")
    raw_df = pd.read_csv(raw_file, usecols=["passenger_count", "trip_distance", 
                                           "fare_amount", "pickup_datetime"])
    
    print(f"Reading processed data from {processed_file}...")
    proc_df = pd.read_csv(processed_file)
    
    # Check if all trip IDs are unique
    trip_ids = proc_df["trip_id"].tolist()
    unique_ids = set(trip_ids)
    
    if len(trip_ids) != len(unique_ids):
        print("NO - Found duplicate IDs")
        sys.exit(1)
    
    # Verify all ID characters are uppercase alphabetic
    invalid_ids = [id for id in trip_ids if not (len(id) == 6 and id.isalpha() and id.isupper())]
    
    if invalid_ids:
        print("NO - Found IDs with invalid format")
        sys.exit(1)
    
    # Check row count
    if len(raw_df) != len(proc_df):
        print("NO - Row count mismatch")
        sys.exit(1)
    
    # Check numeric columns for exact matches
    numeric_cols = ["passenger_count", "trip_distance", "fare_amount"]
    
    for col in numeric_cols:
        # Convert to same dtype for comparison
        raw_values = raw_df[col].astype(float).tolist()
        proc_values = proc_df[col].astype(float).tolist()
        
        mismatches = sum(1 for a, b in zip(raw_values, proc_values) if abs(a - b) > 1e-10)
        
        if mismatches != 0:
            print(f"NO - Found mismatches in '{col}' column")
            sys.exit(1)
    
    # Check datetime conversion
    raw_times = []
    for dt_str in raw_df["pickup_datetime"]:
        try:
            dt = datetime.strptime(dt_str, '%m/%d/%Y %I:%M:%S %p')
            raw_times.append(dt.strftime('%H:%M:%S'))
        except ValueError:
            print("NO - Could not parse datetime")
            sys.exit(1)
    
    proc_times = proc_df["pickup_datetime"].tolist()
    
    time_mismatches = sum(1 for a, b in zip(raw_times, proc_times) if a != b)
    
    if time_mismatches != 0:
        print("NO - Incorrect datetime conversions")
        sys.exit(1)
    
    # If we reached here, everything passed
    print("YES - All data verified correctly")

if __name__ == "__main__":
    raw_file = "Raw Data.csv"
    processed_file = "relevantdata.csv"
    verify_data(raw_file, processed_file) 