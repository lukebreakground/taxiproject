#!/usr/bin/env python3
import pandas as pd
from datetime import datetime
import sys

def verify_extract(raw_file, processed_file):
    """
    Verify that no data was lost or modified during extraction process
    (except for datetime format)
    
    Args:
        raw_file: Path to the original raw data CSV
        processed_file: Path to the processed data CSV
    """
    print(f"Reading raw data from {raw_file}...")
    raw_df = pd.read_csv(raw_file, usecols=["passenger_count", "trip_distance", 
                                           "fare_amount", "pickup_datetime", "dropoff_datetime"])
    
    print(f"Reading processed data from {processed_file}...")
    proc_df = pd.read_csv(processed_file)
    
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
    
    # Check datetime conversions
    datetime_cols = ["pickup_datetime", "dropoff_datetime"]
    
    for dt_col in datetime_cols:
        raw_times = []
        for dt_str in raw_df[dt_col]:
            try:
                dt = datetime.strptime(dt_str, '%m/%d/%Y %I:%M:%S %p')
                raw_times.append(dt.strftime('%H:%M:%S'))
            except ValueError:
                print(f"NO - Could not parse datetime in {dt_col}")
                sys.exit(1)
        
        proc_times = proc_df[dt_col].tolist()
        
        time_mismatches = sum(1 for a, b in zip(raw_times, proc_times) if a != b)
        
        if time_mismatches != 0:
            print(f"NO - Incorrect datetime conversions in {dt_col}")
            sys.exit(1)
    
    # If we reached here, everything passed
    print("YES - All extraction data verified correctly")

def verify_format(relevant_file, formatted_file):
    """
    Verify that:
    1. No data was lost (except datetime columns which are intentionally removed)
    2. All trip IDs are unique
    3. Elapsed time calculation is correct
    
    Args:
        relevant_file: Path to the relevant data CSV
        formatted_file: Path to the formatted data CSV with IDs and elapsed time
    """
    print(f"Reading relevant data from {relevant_file}...")
    rel_df = pd.read_csv(relevant_file)
    
    print(f"Reading formatted data from {formatted_file}...")
    fmt_df = pd.read_csv(formatted_file)
    
    # Check if all trip IDs are unique
    trip_ids = fmt_df["trip_id"].tolist()
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
    if len(rel_df) != len(fmt_df):
        print("NO - Row count mismatch")
        sys.exit(1)
    
    # Check that expected columns are preserved (except datetime columns)
    expected_cols = [col for col in rel_df.columns if col not in ['pickup_datetime', 'dropoff_datetime']]
    for col in expected_cols:
        if col not in fmt_df.columns:
            print(f"NO - Missing column {col} in formatted data")
            sys.exit(1)
    
    # Verify the datetime columns are removed
    for col in ['pickup_datetime', 'dropoff_datetime']:
        if col in fmt_df.columns:
            print(f"NO - Column {col} should be removed from formatted data")
            sys.exit(1)
    
    # Verify elapsed time calculations by recalculating from the relevant data
    print("Verifying elapsed time calculations...")
    
    # We need to obtain the original datetime values from the relevant data file
    rel_df_times = pd.read_csv(relevant_file)
    
    errors = 0
    for i, (_, rel_row) in enumerate(rel_df_times.iterrows()):
        fmt_row = fmt_df.iloc[i]  # Get the corresponding row in the formatted dataframe
        
        pickup = datetime.strptime(rel_row['pickup_datetime'], '%H:%M:%S')
        dropoff = datetime.strptime(rel_row['dropoff_datetime'], '%H:%M:%S')
        
        # If dropoff is earlier than pickup (crossing midnight), add a day
        if dropoff < pickup:
            from datetime import timedelta
            dropoff = dropoff + timedelta(days=1)
        
        expected_elapsed = (dropoff - pickup).total_seconds()
        actual_elapsed = fmt_row['elapsed_time']
        
        if abs(expected_elapsed - actual_elapsed) > 1e-10:
            errors += 1
            if errors <= 5:  # Only show the first 5 errors
                print(f"Error in elapsed time calculation for row {i}:")
                print(f"  Pickup: {rel_row['pickup_datetime']}, Dropoff: {rel_row['dropoff_datetime']}")
                print(f"  Expected: {expected_elapsed}, Actual: {actual_elapsed}")
    
    if errors > 0:
        print(f"NO - Found {errors} errors in elapsed time calculations")
        sys.exit(1)
    
    # If we reached here, everything passed
    print("YES - All formatting data verified correctly")

if __name__ == "__main__":
    raw_file = "raw_data.csv"
    relevant_file = "relevant_data.csv"
    formatted_file = "formatted_data.csv"
    
    print("Verifying extraction process...")
    verify_extract(raw_file, relevant_file)
    
    print("\nVerifying formatting process...")
    verify_format(relevant_file, formatted_file) 