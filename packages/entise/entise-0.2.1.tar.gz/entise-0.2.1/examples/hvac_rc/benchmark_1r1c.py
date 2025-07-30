"""
Benchmark script for HVAC: 1r1c

This script tests the performance of the 1R1C method with 100 HVAC objects.
It generates 100 HVAC objects with varying parameters, uses the R1C1 method
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

def generate_hvac_objects(num_objects=100, seed=42):
    """
    Generate HVAC objects with varying parameters.
    
    Args:
        num_objects (int): Number of HVAC objects to generate
        seed (int): Random seed for reproducibility
        
    Returns:
        pd.DataFrame: DataFrame containing HVAC objects
    """
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    # Create a list to store the objects
    objects_list = []
    
    # Generate objects with varying parameters
    for i in range(num_objects):
        # Generate random variations for parameters
        # Thermal resistance (K/W) - typical range from 0.0002 to 0.004
        resistance = np.random.uniform(0.0002, 0.004)
        
        # Thermal capacitance (J/K) - typical range from 10M to 350M
        capacitance = np.random.uniform(10e6, 350e6)
        
        # Ventilation rate (W/K) - typically scales with building size
        ventilation = capacitance * np.random.uniform(1e-6, 5e-6)
        
        # Temperature setpoints (°C)
        temp_init = np.random.uniform(18, 22)
        temp_min = np.random.uniform(18, 22)
        temp_max = np.random.uniform(22, 26)
        
        # Latitude and longitude (small variations around a base location)
        latitude = 49.72 + np.random.uniform(-0.01, 0.01)
        longitude = 11.05 + np.random.uniform(-0.01, 0.01)
        
        # Heated area (m²) - typical range from 100 to 5000
        heated_area = np.random.uniform(100, 5000)
        
        # Internal gains - either a constant value or a reference to a data source
        # For simplicity, we'll use a 50/50 split between constant values and data references
        if np.random.random() < 0.5:
            gains_internal = np.random.uniform(100, 1000)  # Constant value in W
            gains_internal_column = ""
        else:
            gains_internal = "internal_gains"  # Reference to data source
            # Choose a random column from available options
            column_options = ["residential", "office", "commercial", "industrial"]
            gains_internal_column = np.random.choice(column_options)
        
        # Create the object
        obj = {
            'id': f'hvac_{i+1}',
            'hvac': '1R1C',
            'weather': 'weather',
            'resistance': resistance,
            'capacitance': capacitance,
            'ventilation': ventilation,
            'temp_init': temp_init,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'windows': 'windows',
            'latitude': latitude,
            'longitude': longitude,
            'heated_area': heated_area,
            'gains_internal': gains_internal,
            'gains_internal_column': gains_internal_column
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
        num_objects (int): Number of HVAC objects to generate
        workers (int): Number of workers to use for parallel processing
        visualize (bool): Whether to visualize the results
        
    Returns:
        tuple: A tuple containing:
            - execution_time (float): Execution time in seconds
            - summary (pd.DataFrame): Summary statistics
            - timeseries (dict): Time series data
    """
    # Generate HVAC objects
    print(f"Generating {num_objects} HVAC objects...")
    objects = generate_hvac_objects(num_objects)
    
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
    print("Summary [Wh] | [W]:")
    summary_subset = summary.filter(regex=f'(demand|load_max)_(heating|cooling)')
    print(summary_subset.head())  # Print only the first few rows
    
    # Visualize results if requested
    if visualize:
        # Convert index to datetime for all time series
        for obj_id in df:
            if Types.HVAC in df[obj_id]:
                df[obj_id][Types.HVAC].index = pd.to_datetime(df[obj_id][Types.HVAC].index)
        
        # Get building parameters from objects dataframe
        building_configs = {}
        for _, row in objects.iterrows():
            obj_id = row['id']
            if obj_id in df and Types.HVAC in df[obj_id]:
                building_configs[obj_id] = {
                    'resistance': row['resistance'],
                    'capacitance': row['capacitance'],
                    'temp_min': row['temp_min'],
                    'temp_max': row['temp_max'],
                    'heated_area': row['heated_area']
                }
        
        # Figure 1: Histogram of total heating demand
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        total_heating = [summary.loc[obj_id, f'demand_{Types.HEATING}'] / 1000 for obj_id in df if obj_id in summary.index]  # Convert to kWh
        plt.hist(total_heating, bins=20)
        plt.title('Histogram of Total Heating Demand')
        plt.xlabel('Total Heating Demand (kWh)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        # Figure 2: Histogram of total cooling demand
        plt.subplot(1, 2, 2)
        total_cooling = [summary.loc[obj_id, f'demand_{Types.COOLING}'] / 1000 for obj_id in df if obj_id in summary.index]  # Convert to kWh
        plt.hist(total_cooling, bins=20)
        plt.title('Histogram of Total Cooling Demand')
        plt.xlabel('Total Cooling Demand (kWh)')
        plt.ylabel('Count')
        plt.grid(axis='y')
        
        plt.tight_layout()
        plt.show()
        
        # Figure 3: Sample of indoor temperature profiles for a few buildings
        plt.figure(figsize=(12, 8))
        sample_ids = list(df.keys())[:5]  # Take first 5 buildings
        
        for i, obj_id in enumerate(sample_ids):
            if Types.HVAC in df[obj_id]:
                # Get a sample day (e.g., a winter day)
                sample_day = df[obj_id][Types.HVAC].loc['2022-01-15'].copy()
                
                # Get building parameters for the title
                building_params = building_configs[obj_id] if obj_id in building_configs else {}
                
                # Plot the indoor temperature profile
                plt.subplot(len(sample_ids), 1, i+1)
                plt.plot(sample_day.index.hour, sample_day['temp_in'], label='Indoor Temperature')
                
                # Add horizontal lines for min and max temperature setpoints
                if 'temp_min' in building_params and 'temp_max' in building_params:
                    plt.axhline(y=building_params['temp_min'], color='r', linestyle='--', alpha=0.5, label='Min Temp')
                    plt.axhline(y=building_params['temp_max'], color='b', linestyle='--', alpha=0.5, label='Max Temp')
                
                plt.title(f'ID {obj_id}, Heated Area: {building_params.get("heated_area", 0):.0f} m²')
                plt.xlabel('Hour of Day')
                plt.ylabel('Temperature (°C)')
                plt.grid(True)
                plt.xticks(range(0, 24, 2))
                plt.legend()
        
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