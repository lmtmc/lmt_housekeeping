from pathlib import Path
from typing import Set

import numpy as np
import datetime
import os
import pandas as pd
import yaml
import xarray as xr
import pickle
config_path = "./config.yaml"
def load_config(config_path):
    try:
        with open(config_path, 'r') as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        return None

config = load_config(config_path)
fixed_directories = config['fixed_directories']


def filter_dataframe_by_time(df, hours=0, start_date=None, end_date=None):
    """
    Filters a DataFrame by the most recent hours or a specified date range.

    Parameters:
    - df (pd.DataFrame): The DataFrame to filter, with a 'time' column in datetime format.
    - hours (int): Number of recent hours to filter by. If greater than 0, it overrides start_date and end_date.
    - start_date (str or pd.Timestamp): The start date to filter from (inclusive).
    - end_date (str or pd.Timestamp): The end date to filter up to (inclusive).

    Returns:
    - filtered_df (pd.DataFrame): The filtered DataFrame.
    """

    # Ensure the 'time' column is in datetime format
    df['time'] = pd.to_datetime(df['time'], utc=True)

    # Filter by recent hours if specified
    if hours > 0:
        recent_time = df['time'].iloc[-1] - pd.Timedelta(hours=hours)
        filtered_df = df[df['time'] >= recent_time]

    # Filter by start_date and end_date if provided
    elif start_date and end_date:
        start_date = pd.to_datetime(start_date, utc=True)
        end_date = pd.to_datetime(end_date, utc=True)
        filtered_df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]

    # Return the full DataFrame if no conditions are met
    else:
        filtered_df = df

    return filtered_df

def load_cache(id_prefix):
    """Load processed data cache from disk, or create a new one if not available."""
    cache_file_path = Path(f'./cache/{id_prefix}.pkl')
    # Check if file exists and has a size greater than 0
    if os.path.exists(cache_file_path) and os.path.getsize(cache_file_path) > 0:
        try:
            with open(cache_file_path, 'rb') as f:
                return pickle.load(f)
        except EOFError:
            print(f"Warning: Cache file {cache_file_path} is empty or corrupted. Recreating the cache.")
            return None  # Return None to indicate cache is not available
    else:
        print(f"No cache found at {cache_file_path} or cache is empty. Recreating cache.")
        return None

def save_cache(cache, id_prefix):
    """Save the processed data cache to disk."""
    try:
        path = Path(f'./cache/{id_prefix}.pkl')
        with path.open('wb') as f:
            pickle.dump(cache, f)
        print(f"Cache saved to {path}")
    except Exception as e:
        print(f"Error saving cache: {e}")


def load_all_data(id_prefix):
    """
    Load and process all .nc files in the directory, using cache when possible.

    Args:
        id_prefix: Identifier used to locate directory and cache file

    Returns:
        Tuple containing:
        - List of disabled (unavailable) days
        - Minimum timestamp across all files
        - Maximum timestamp across all files
    """
    try:
        # Get directory path and verify it exists
        directory = fixed_directories.get(id_prefix)
        if not directory or not os.path.exists(directory):
            print(f"Directory not found for {id_prefix}")
            return [], pd.Timestamp.min, pd.Timestamp.min

        # Load existing cache or create new one
        processed_data_cache = load_cache(id_prefix) or {}
        # Initialize tracking variables
        min_time, max_time = pd.Timestamp.max, pd.Timestamp.min
        available_days=[]
        cache_updated = False

        # Get list of .nc files
        nc_files = [f for f in os.listdir(directory) if f.endswith('.nc')]
        if not nc_files:
            print(f"No .nc files found in {directory}")
            return [], pd.Timestamp.min, pd.Timestamp.min

        # Process each file
        for file in nc_files:
            try:
                file_path = os.path.join(directory, file)
                file_mtime = os.path.getmtime(file_path)

                # Check if file is in cache and cache entry is valid
                cache_entry = processed_data_cache.get(file, {})
                if (file in processed_data_cache and
                        isinstance(cache_entry, dict) and
                        cache_entry.get('mtime') == file_mtime and
                        all(key in cache_entry for key in ['min_time', 'max_time', 'available_days'])):

                    file_min_time = cache_entry['min_time']
                    file_max_time = cache_entry['max_time']
                    file_available_days = cache_entry['available_days']

                    # Validate cached timestamps
                    if not isinstance(file_min_time, pd.Timestamp) or not isinstance(file_max_time, pd.Timestamp):
                        raise ValueError("Invalid timestamp data in cache")

                else:
                    # Process the file
                    file_min_time, file_max_time, file_available_days = process_file(file_path)

                    # Only update cache if we got valid data
                    if file_available_days:
                        processed_data_cache[file] = {
                            'mtime': file_mtime,
                            'min_time': file_min_time,
                            'max_time': file_max_time,
                            'available_days': file_available_days
                        }
                        cache_updated = True

                # Update global tracking variables if we have valid data
                if file_available_days:
                    min_time = min(min_time, file_min_time)
                    max_time = max(max_time, file_max_time)
                    available_days.extend(file_available_days)

            except Exception as e:
                print(f"Error processing file {file}: {e}")
                continue

        # Save cache if it was updated
        if cache_updated:
            print(f'Saving updated cache for {id_prefix}')
            save_cache(processed_data_cache, id_prefix)

        # Calculate disabled days
        if min_time != pd.Timestamp.max and max_time != pd.Timestamp.min:
            try:
                all_days = set(pd.date_range(start=min_time, end=max_time).date)

                disabled_days = sorted(list(all_days - set(available_days)))
            except Exception as e:
                print(f"Error calculating disabled days: {e}")
                disabled_days = []
        else:
            disabled_days = []
        return disabled_days, min_time, max_time

    except Exception as e:
        print(f"Error in load_all_data for {id_prefix}: {e}")
        return [], pd.Timestamp.min, pd.Timestamp.min

def process_file(file_path):
    """Process an individual .nc file to extract min_time, max_time, and available days."""
    min_time, max_time = pd.Timestamp.max, pd.Timestamp.min
    available_days = set()
    if 'thermetry_' in file_path:
        try:
            # Load the dataset
            ds = xr.open_dataset(file_path)

            # Iterate over all 16 channels (assuming time variables are Time1, Time2, ..., Time16)
            for i in range(1, 17):
                time_var = f'Data.ToltecThermetry.Time{i}'
                if time_var in ds.variables:
                    # get data where time is greater than 0
                    time_data = ds[time_var].values
                    time_data = time_data[time_data > 0]

                    if len(time_data) == 0:
                        continue  # Skip if no data for this channel

                    # Convert to pandas datetime
                    timestamps = pd.to_datetime(time_data, unit='s')

                    # Update min and max time for this channel
                    min_time = min(min_time, timestamps.min())
                    max_time = max(max_time, timestamps.max())

                    # Normalize timestamps to date and update available days
                    available_days.update(timestamps.normalize().date)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    elif 'dilutionFridge_' in file_path:
        try:
            # Load the dataset
            ds = xr.open_dataset(file_path)

            # Get the time variable
            time_var = 'Data.ToltecDilutionFridge.SampleTime'
            if time_var in ds.variables:
                # get data where time is greater than 0
                time_data = ds[time_var].values
                time_data = time_data[time_data > 0]

                if len(time_data) == 0:
                    return min_time, max_time, available_days  # Skip if no data

                # Convert to pandas datetime
                timestamps = pd.to_datetime(time_data, unit='s')

                # Update min and max time
                min_time = timestamps.min()
                max_time = timestamps.max()

                # Normalize timestamps to date and update available days
                available_days.update(timestamps.normalize().date)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    elif 'cryocmp_' in file_path:
        try:
            # Load the dataset
            ds = xr.open_dataset(file_path)

            # Get the time variable
            time_var = 'Data.ToltecCryocmp.Time'
            if time_var in ds.variables:

                # get data where time is greater than 0
                time_data = ds[time_var].values
                time_data = time_data[time_data > 0]

                if len(time_data) == 0:
                    return min_time, max_time, available_days  # Skip if no data

                # Convert to pandas datetime
                timestamps = pd.to_datetime(time_data, unit='s')

                # Update min and max time
                min_time = min(min_time, timestamps.min())
                max_time = max(max_time, timestamps.max())
                # Normalize timestamps to date and update available days
                available_days.update(timestamps.normalize().date)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    elif 'rsfend_' in file_path:
        try:
            # Load the dataset
            ds = xr.open_dataset(file_path)

            # Get the time variable
            time_var = 'Data.Rsfend.Time'
            if time_var in ds.variables:
                # get data where time is greater than 0
                time_data = ds[time_var].values
                time_data = time_data[time_data > 0]

                if len(time_data) == 0:
                    return min_time, max_time, available_days  # Skip if no data

                # Convert to pandas datetime
                timestamps = pd.to_datetime(time_data, unit='s')

                # Update min and max time
                min_time = min(min_time, timestamps.min())
                max_time = max(max_time, timestamps.max())

                # Normalize timestamps to date and update available days
                available_days.update(timestamps.normalize().date)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    else:
        print(f"Unsupported file type: {file_path}")

    return min_time, max_time, available_days

# if start_date == end_date get all the files that contain the start_date
# if start_date != end_date get all the files that has available date between the start_date and end_date
# return a list containing the file names
def get_files(id_prefix, hours, start_date, end_date):
    # Load existing cache (if any)
    processed_data_cache = load_cache(id_prefix)

    # if hours is 0 then the start_date and end_date are dates from the date picker, else date is more max_time
    if hours == 0:
        start_date = pd.Timestamp(start_date).date()
        end_date = pd.Timestamp(end_date).date()
    else:
        # get the data in the last file that was processed
        end_date = load_all_data(id_prefix)[2].date()
        start_date = end_date
    # Initialize data dictionary
    files = []
    for file, metadata in processed_data_cache.items():
        min_time = metadata['min_time'].date()
        max_time = metadata['max_time'].date()
        if start_date == end_date:
            if min_time <= start_date <= max_time:
                files.append(file)
            else:
                continue
        else:
            if metadata['available_days'] & set(pd.date_range(start=start_date, end=end_date).date):
                files.append(file)
    return files

