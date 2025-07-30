"""
Benchmark script for DHW: jordanvajen

This script tests the performance of the Jordan & Vajen method with 100 DHW objects.
It generates 100 DHW objects with varying parameters, uses the JordanVajen method
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
from entise.constants import Types, Objects as O

def generate_dhw_objects(num_objects=100, seed=42):
    """
    Generate DHW objects with varying parameters.
    
    Args:
        num_objects (int): Number of DHW objects to generate
        seed (int): Random seed for reproducibility
        
    Returns:
        pd.DataFrame: DataFrame containing DHW objects
    """
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    # Create a list to store the objects
    objects_list = []
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        dwelling_size = np.random.randint(50, 300)  # Dwelling size between 50 and 300 m²
        temp_cold = np.random.uniform(5, 15)  # Cold water temperature between 5 and 15°C
        temp_hot = np.random.uniform(45, 65)  # Hot water temperature between 45 and 65°C
        
        # List of possible holiday locations
        holiday_locations = [
            None, "DE", "FR", "IT", "ES", "UK", "US", "CA", "AU", "JP", 
            "BR", "MX", "PT", "NL", "BE", "AT", "CH", "SE", "NO", "DK"
        ]
        holidays_location = np.random.choice(holiday_locations)
        
        # Create the object
        obj = {
            'id': f'dhw_{i+1}',
            'dhw': 'jordanvajen',
            'datetimes': 'weather',
            'dwelling_size': dwelling_size,
            'temp_water_cold': temp_cold,
            'temp_water_hot': temp_hot,
            'holidays_location': holidays_location,
            'seed': i  # Use different seed for each object
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
        num_objects (int): Number of DHW objects to generate
        workers (int): Number of workers to use for parallel processing
        visualize (bool): Whether to visualize the results
        
    Returns:
        tuple: A tuple containing:
            - execution_time (float): Execution time in seconds
            - summary (pd.DataFrame): Summary statistics
            - timeseries (dict): Time series data
    """
    # Generate DHW objects
    print(f"Generating {num_objects} DHW objects...")
    objects = generate_dhw_objects(num_objects)
    
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
    print("Summary [liters] | [kWh] | [W]:")
    summary_subset = summary.filter(regex=f'{Types.DHW}')
    print(summary_subset.head())  # Print only the first few rows
    
    # Visualize results if requested
    if visualize:
        # Convert index to datetime for all time series
        for obj_id in df:
            if Types.DHW in df[obj_id]:
                df[obj_id][Types.DHW].index = pd.to_datetime(df[obj_id][Types.DHW].index)
        
        # Get dwelling size values from objects dataframe
        system_configs = {}
        for _, row in objects.iterrows():
            obj_id = row['id']
            if obj_id in df and Types.DHW in df[obj_id]:
                dwelling_size = row['dwelling_size']
                temp_cold = row['temp_water_cold']
                temp_hot = row['temp_water_hot']
                system_configs[obj_id] = {
                    'dwelling_size': dwelling_size,
                    'temp_cold': temp_cold,
                    'temp_hot': temp_hot
                }
        
        # Figure 1: Histogram of total volume demand
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        total_volume = [summary.loc[obj_id, f'demand_{Types.DHW}_volume_total'] for obj_id in df if obj_id in summary.index]
        plt.hist(total_volume, bins=20)
        plt.title('Histogram of Total DHW Volume Demand')
        plt.xlabel('Total Volume (liters)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        # Figure 2: Histogram of total energy demand
        plt.subplot(1, 2, 2)
        total_energy = [summary.loc[obj_id, f'demand_{Types.DHW}_energy_total'] / 1000 for obj_id in df if obj_id in summary.index]  # Convert to kWh
        plt.hist(total_energy, bins=20)
        plt.title('Histogram of Total DHW Energy Demand')
        plt.xlabel('Total Energy (kWh)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        plt.tight_layout()
        plt.show()
        
        # Figure 3: Sample of daily profiles for a few systems
        plt.figure(figsize=(12, 8))
        sample_ids = list(df.keys())[:5]  # Take first 5 systems
        
        for i, obj_id in enumerate(sample_ids):
            if Types.DHW in df[obj_id]:
                # Get a sample day
                sample_day = df[obj_id][Types.DHW].loc['2022-06-15'].copy()
                
                # Get dwelling size for the title
                dwelling_size = system_configs[obj_id]['dwelling_size'] if obj_id in system_configs else 0
                
                # Plot the daily profile
                plt.subplot(len(sample_ids), 1, i+1)
                plt.plot(sample_day.index.hour, sample_day[f'load_{Types.DHW}_volume'], label='Volume (liters)')
                plt.title(f'ID {obj_id}, Dwelling Size: {dwelling_size} m²')
                plt.xlabel('Hour of Day')
                plt.ylabel('Volume (liters)')
                plt.grid(True)
                plt.xticks(range(0, 24, 2))
                plt.legend()
        
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