#!/usr/bin/env python3

import pandas as pd
import numpy as np
from scipy import stats
import os
from datetime import datetime

def calculate_statistics(data):
    """
    Calculate all descriptive statistics for each numerical column in the dataframe
    
    Args:
        data (pandas.DataFrame): The dataframe to analyze
        
    Returns:
        dict: Dictionary containing statistics for each numerical column
    """
    # Get numerical columns only
    numerical_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    stats_dict = {}
    
    for col in numerical_cols:
        col_data = data[col].dropna()
        
        if len(col_data) == 0:
            continue
            
        # Create a dictionary for each column
        col_stats = {}
        
        # Central Tendency
        col_stats['mean'] = col_data.mean()
        col_stats['median'] = col_data.median()
        col_stats['mode'] = col_data.mode().iloc[0] if not col_data.mode().empty else None
        
        # Dispersion (Spread)
        col_stats['range'] = col_data.max() - col_data.min()
        col_stats['variance'] = col_data.var()
        col_stats['std_dev'] = col_data.std()
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        col_stats['iqr'] = q3 - q1
        
        # Position
        col_stats['min'] = col_data.min()
        col_stats['max'] = col_data.max()
        col_stats['q1'] = q1
        col_stats['q2'] = col_data.quantile(0.5)  # Same as median
        col_stats['q3'] = q3
        col_stats['p10'] = col_data.quantile(0.1)
        col_stats['p90'] = col_data.quantile(0.9)
        
        # Shape
        col_stats['skewness'] = stats.skew(col_data)
        col_stats['kurtosis'] = stats.kurtosis(col_data)
        
        stats_dict[col] = col_stats
    
    return stats_dict

def generate_markdown_report(stats_dict, output_file):
    """
    Generate a markdown report from the statistics dictionary with columns as headers
    and statistics as rows in a single consolidated table
    
    Args:
        stats_dict (dict): Dictionary containing statistics for each column
        output_file (str): Path to save the markdown report
    """
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"# Descriptive Statistics Report\n\n")
        f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Write summary info
        f.write(f"## Summary\n\n")
        f.write(f"This report contains descriptive statistics for the numerical columns in the dataset.\n\n")
        f.write(f"Number of numerical columns analyzed: {len(stats_dict)}\n\n")
        
        # Get all column names
        columns = list(stats_dict.keys())
        
        # Define all statistics to include in the report
        all_stats = [
            # Central Tendency
            "mean", "median", "mode",
            # Dispersion (Spread)
            "range", "variance", "std_dev", "iqr",
            # Position
            "min", "max", "q1", "q2", "q3", "p10", "p90",
            # Shape
            "skewness", "kurtosis"
        ]
        
        descriptions = {
            "mean": "Average value",
            "median": "Middle value when ordered",
            "mode": "Most frequent value",
            "range": "Difference between max and min",
            "variance": "Average squared deviation from the mean",
            "std_dev": "Square root of variance (spread around mean)",
            "iqr": "Middle 50% spread (Q3 - Q1)",
            "min": "Smallest value",
            "max": "Largest value",
            "q1": "First quartile (25th percentile)",
            "q2": "Second quartile (50th percentile, median)",
            "q3": "Third quartile (75th percentile)",
            "p10": "10th percentile",
            "p90": "90th percentile",
            "skewness": "Measure of asymmetry (>0: right skew, <0: left skew)",
            "kurtosis": "Measure of 'tailedness' (>0: heavy tails, <0: light tails)"
        }
        
        # Create a single consolidated table
        f.write("## Descriptive Statistics\n\n")
        
        # Create table header with column names
        header = "| Statistic | " + " | ".join(columns) + " | Description |\n"
        separator = "|-----------|" + "|".join(["-----------" for _ in columns]) + "|-------------|\n"
        f.write(header)
        f.write(separator)
        
        # Add rows for each statistic
        for stat in all_stats:
            row = f"| {stat.replace('_', ' ').title()} | "
            for col in columns:
                value = stats_dict[col][stat]
                # Format numbers with appropriate precision
                if isinstance(value, (int, float)):
                    if abs(value) < 0.01 or abs(value) > 1000:
                        row += f"{value:.4e} | "
                    else:
                        row += f"{value:.4f} | "
                else:
                    row += f"{value} | "
            row += f"{descriptions[stat]} |\n"
            f.write(row)
        
        f.write("\n")
        
        # Add interpretations section
        f.write("## Interpretations\n\n")
        
        for col in columns:
            skewness = stats_dict[col]['skewness']
            kurtosis = stats_dict[col]['kurtosis']
            
            # Interpret skewness
            if skewness > 0.5:
                skew_interp = "strong positive skew (right-tailed)"
            elif skewness > 0.1:
                skew_interp = "moderate positive skew"
            elif skewness < -0.5:
                skew_interp = "strong negative skew (left-tailed)"
            elif skewness < -0.1:
                skew_interp = "moderate negative skew"
            else:
                skew_interp = "approximately symmetric"
            
            # Interpret kurtosis
            if kurtosis > 1:
                kurt_interp = "very heavy tails (more outliers than normal)"
            elif kurtosis > 0.5:
                kurt_interp = "heavy tails"
            elif kurtosis < -1:
                kurt_interp = "very light tails (fewer outliers than normal)"
            elif kurtosis < -0.5:
                kurt_interp = "light tails"
            else:
                kurt_interp = "near normal tails"
            
            f.write(f"### {col}\n\n")
            f.write(f"The distribution is {skew_interp} with {kurt_interp}.\n\n")

def main():
    """Main function to process the CSV and generate the report"""
    # File paths
    input_file = 'formatted_data.csv'
    output_file = 'statistics_report.md'
    
    print(f"Reading data from {input_file}...")
    
    # Read the CSV file
    try:
        data = pd.read_csv(input_file)
        print(f"Successfully read data with {data.shape[0]} rows and {data.shape[1]} columns")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Calculate statistics
    print("Calculating statistics...")
    stats_dict = calculate_statistics(data)
    
    # Generate markdown report
    print(f"Generating markdown report to {output_file}...")
    generate_markdown_report(stats_dict, output_file)
    
    print(f"Report successfully generated: {output_file}")

if __name__ == "__main__":
    main() 