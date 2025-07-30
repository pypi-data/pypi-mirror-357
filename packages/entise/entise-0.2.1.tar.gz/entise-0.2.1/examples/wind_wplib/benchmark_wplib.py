"""
Benchmark script for Wind: wplib

This script tests the performance of the wplib method with 100 wind turbine objects.
It generates 100 wind turbine objects with varying parameters, uses the WPLib method
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

def generate_wind_objects(num_objects=100):
    """
    Generate wind turbine objects with varying parameters.
    
    Args:
        num_objects (int): Number of wind turbine objects to generate
        
    Returns:
        pd.DataFrame: DataFrame containing wind turbine objects
    """
    # Create a list to store the objects
    objects_list = []
    
    # Define a list of common turbine types from windpowerlib
    turbine_types = [
        "SWT130/3600",  # Siemens
        "V164/8000",    # Vestas
        "E-101/3500",   # Enercon
        "GE130/3200",   # GE Wind
        "N117/2400",    # Nordex
        "S122/3200",    # Senvion/REpower
        "AD116/5000",   # Adwen/Areva
        "SWT142/3150"   # Siemens
    ]
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        power = np.random.randint(1000000, 8000000)  # Power between 1MW and 8MW
        turbine_type = np.random.choice(turbine_types)
        hub_height = np.random.randint(80, 180)  # Hub height between 80m and 180m
        
        # Create the object
        obj = {
            'id': f'wind_{i+1}',
            'wind': 'wplib',
            'weather': 'weather',
            'power': power,
            'turbine_type': turbine_type,
            'hub_height': hub_height
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
        num_objects (int): Number of wind turbine objects to generate
        workers (int): Number of workers to use for parallel processing
        visualize (bool): Whether to visualize the results
        
    Returns:
        tuple: A tuple containing:
            - execution_time (float): Execution time in seconds
            - summary (pd.DataFrame): Summary statistics
            - timeseries (dict): Time series data
    """
    # Generate wind turbine objects
    print(f"Generating {num_objects} wind turbine objects...")
    objects = generate_wind_objects(num_objects)
    
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
    print("Summary [MWh/a] | [MW] | [h]:")
    summary_mwh = summary.copy()
    summary_mwh['generation_wind'] /= 1e6  # Convert Wh to MWh
    summary_mwh['maximum_generation_wind'] /= 1e6  # Convert W to MW
    summary_mwh = summary_mwh.round(2)
    print(summary_mwh.head())  # Print only the first few rows
    
    # Visualize results if requested
    if visualize:
        # Convert index to datetime for all time series
        for obj_id in df:
            df[obj_id][Types.WIND].index = pd.to_datetime(df[obj_id][Types.WIND].index)
        
        # Get turbine parameters from objects dataframe
        system_configs = {}
        for _, row in objects.iterrows():
            obj_id = row['id']
            if obj_id in df:
                turbine_type = row['turbine_type'] if not pd.isna(row.get('turbine_type', pd.NA)) else "Default"
                hub_height = row['hub_height'] if not pd.isna(row.get('hub_height', pd.NA)) else "Default"
                power = row['power'] if not pd.isna(row['power']) else 1
                system_configs[obj_id] = {
                    'turbine_type': turbine_type,
                    'hub_height': hub_height,
                    'power': power
                }
        
        # Figure 1: Histogram of maximum generation
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        max_gen = [df[obj_id][Types.WIND].max().iloc[0] for obj_id in df]
        plt.hist(max_gen, bins=20)
        plt.title('Histogram of Maximum Wind Power Generation')
        plt.xlabel('Maximum Power (W)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        # Figure 2: Histogram of total generation
        plt.subplot(1, 2, 2)
        total_gen = [df[obj_id][Types.WIND].sum().iloc[0] / 1000 for obj_id in df]  # Convert to kWh
        plt.hist(total_gen, bins=20)
        plt.title('Histogram of Total Annual Wind Power Generation')
        plt.xlabel('Total Generation (kWh)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        plt.tight_layout()
        plt.show()
        
        # Figure 3: Sample of daily profiles for a few systems
        plt.figure(figsize=(12, 8))
        sample_ids = list(df.keys())[:5]  # Take first 5 systems
        
        for i, obj_id in enumerate(sample_ids):
            # Get a sample day
            sample_day = df[obj_id][Types.WIND].iloc[:24].copy()
            
            # Get turbine parameters for the title
            turbine_type = system_configs[obj_id]['turbine_type'] if obj_id in system_configs else "Default"
            hub_height = system_configs[obj_id]['hub_height'] if obj_id in system_configs else "Default"
            
            # Plot the daily profile
            plt.subplot(len(sample_ids), 1, i+1)
            plt.plot(range(24), sample_day.values)
            plt.title(f'ID {obj_id}, Turbine: {turbine_type}, Hub Height: {hub_height}m')
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
    time_1, _, _ = run_benchmark(num_objects=100, workers=1, visualize=False)
    print(f"Runtime: {time_1:.2f} seconds")
    
    print("\nRunning benchmark with 4 workers...")
    time_4, _, _ = run_benchmark(num_objects=100, workers=4, visualize=False)
    print(f"Runtime: {time_4:.2f} seconds")
    
    # Print speedup
    speedup = time_1 / time_4
    print(f"\nSpeedup with 4 workers: {speedup:.2f}x")
    
    # # Run with visualization for the last run
    # print("\nRunning benchmark with visualization...")
    # _, _, _ = run_benchmark(num_objects=100, workers=4, visualize=True)