"""
Benchmark script for PV: pvlib

This script tests the performance of the pvlib method with 100 PV objects.
It generates 100 PV objects with varying parameters, uses the PVLib method
to generate time series for all objects, and measures the execution time.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the TimeSeriesGenerator
from entise.core.generator import TimeSeriesGenerator
from entise.constants import Types

def generate_pv_objects(num_objects=100, base_latitude=49.72, base_longitude=11.05):
    """
    Generate PV objects with varying parameters.
    
    Args:
        num_objects (int): Number of PV objects to generate
        base_latitude (float): Base latitude for the objects
        base_longitude (float): Base longitude for the objects
        
    Returns:
        pd.DataFrame: DataFrame containing PV objects
    """
    # Create a list to store the objects
    objects_list = []
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        latitude = base_latitude + np.random.uniform(-0.01, 0.01)
        longitude = base_longitude + np.random.uniform(-0.01, 0.01)
        power = np.random.randint(1000, 20000)  # Power between 1kW and 20kW
        azimuth = np.random.randint(0, 360)  # Azimuth between 0 and 360 degrees
        tilt = np.random.randint(0, 90)  # Tilt between 0 and 90 degrees
        
        # Create the object
        obj = {
            'id': f'pv_{i+1}',
            'pv': 'pvlib',
            'latitude': latitude,
            'longitude': longitude,
            'weather': 'weather',
            'power': power,
            'azimuth': azimuth,
            'tilt': tilt,
            'altitude': None,
            'pv_arrays': None
        }
        
        # Add the object to the list
        objects_list.append(obj)
    
    # Convert the list to a DataFrame
    objects_df = pd.DataFrame(objects_list)
    
    return objects_df

def run_benchmark(num_objects=100, workers=1, visualize=False):
    """
    Run the benchmark with the specified number of objects and workers.
    
    Args:
        num_objects (int): Number of PV objects to generate
        workers (int): Number of workers to use for parallel processing
        visualize (bool): Whether to visualize the results
        
    Returns:
        tuple: A tuple containing:
            - execution_time (float): Execution time in seconds
            - summary (pd.DataFrame): Summary statistics
            - timeseries (dict): Time series data
    """
    # Generate PV objects
    print(f"Generating {num_objects} PV objects...")
    objects = generate_pv_objects(num_objects)
    
    # Load data
    print("Loading data...")
    cwd = '.'  # Current working directory
    data = {}
    data_folder = 'data'
    for file in os.listdir(os.path.join(cwd, data_folder)):
        if file.endswith('.csv'):
            name = file.split('.')[0]
            data[name] = pd.read_csv(os.path.join(os.path.join(cwd, data_folder, file)), parse_dates=True)
    print('Loaded data keys:', list(data.keys()))
    
    # Instantiate and configure the generator
    print("Configuring generator...")
    gen = TimeSeriesGenerator()
    gen.add_objects(objects)
    
    # Generate time series and measure execution time
    print(f"Generating time series with {workers} worker(s)...")
    start_time = time.time()
    summary, df = gen.generate(data, workers=workers)
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Print execution time
    print(f"Execution time: {execution_time:.2f} seconds")
    
    # Print summary
    print("Summary [kWh/a] | [Wp] | [h]:")
    summary_kwh = summary.copy()
    summary_kwh['generation_pv'] /= 1000
    summary_kwh = summary_kwh.round(0).astype(int)
    print(summary_kwh.head())  # Print only the first few rows
    
    # Visualize results if requested
    if visualize:
        # Convert index to datetime for all time series
        for obj_id in df:
            df[obj_id][Types.PV].index = pd.to_datetime(df[obj_id][Types.PV].index)
        
        # Get azimuth and tilt values from objects dataframe
        system_configs = {}
        for _, row in objects.iterrows():
            obj_id = row['id']
            if obj_id in df:
                azimuth = row['azimuth'] if not pd.isna(row['azimuth']) else 0
                tilt = row['tilt'] if not pd.isna(row['tilt']) else 0
                power = row['power'] if not pd.isna(row['power']) else 1
                system_configs[obj_id] = {
                    'azimuth': azimuth,
                    'tilt': tilt,
                    'power': power
                }
        
        # Figure 1: Histogram of maximum generation
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        max_gen = [df[obj_id][Types.PV].max().iloc[0] for obj_id in df]
        plt.hist(max_gen, bins=20)
        plt.title('Histogram of Maximum PV Generation')
        plt.xlabel('Maximum Power (W)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        # Figure 2: Histogram of total generation
        plt.subplot(1, 2, 2)
        total_gen = [df[obj_id][Types.PV].sum().iloc[0] / 1000 for obj_id in df]  # Convert to kWh
        plt.hist(total_gen, bins=20)
        plt.title('Histogram of Total Annual PV Generation')
        plt.xlabel('Total Generation (kWh)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        plt.tight_layout()
        plt.show()
        
        # Figure 3: Sample of daily profiles for a few systems
        plt.figure(figsize=(12, 8))
        sample_ids = list(df.keys())[:5]  # Take first 5 systems
        
        for i, obj_id in enumerate(sample_ids):
            # Get a sample day (e.g., a summer day)
            sample_day = df[obj_id][Types.PV].loc['2022-06-15'].copy()
            
            # Get azimuth and tilt values for the title
            azimuth = system_configs[obj_id]['azimuth'] if obj_id in system_configs else 0
            tilt = system_configs[obj_id]['tilt'] if obj_id in system_configs else 0
            
            # Plot the daily profile
            plt.subplot(len(sample_ids), 1, i+1)
            plt.plot(sample_day.index.hour, sample_day.values)
            plt.title(f'ID {obj_id}, Azimuth: {azimuth}, Tilt: {tilt}')
            plt.xlabel('Hour of Day')
            plt.ylabel('Power (W)')
            plt.grid(True)
            plt.xticks(range(0, 24, 2))
        
        plt.tight_layout()
        plt.show()
    
    return execution_time, summary, df

if __name__ == "__main__":
    # Run the benchmark with different numbers of workers
    print("Running benchmark with 1 worker...")
    time_1, _, _ = run_benchmark(num_objects=1000, workers=1, visualize=False)
    print(f"Runtime: {time_1:.2f} seconds")
    
    print("\nRunning benchmark with 4 workers...")
    time_4, _, _ = run_benchmark(num_objects=1000, workers=8, visualize=False)
    print(f"Runtime: {time_4:.2f} seconds")
    
    # Print speedup
    speedup = time_1 / time_4
    print(f"\nSpeedup with 4 workers: {speedup:.2f}x")
    
    # # Run with visualization for the last run
    # print("\nRunning benchmark with visualization...")
    # _, _, _ = run_benchmark(num_objects=100, workers=4, visualize=True)