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
    else:
        print(f"No cache found at {cache_file_path} or cache is empty. Recreating cache.")
    return None

def save_cache(cache, id_prefix):
    """Save the processed data cache to disk."""
    cache_file_path = Path(f'./cache/{id_prefix}.pkl')
    try:
        with cache_file_path.open('wb') as f:
            pickle.dump(cache, f)
        print(f"Cache saved to {cache_file_path}")
    except Exception as e:
        print(f"Error saving cache: {e}")


def load_all_data(id_prefix):
    """
    Load and process all .nc files in the directory, using cache when possible.
    """
    directory = fixed_directories.get(id_prefix)

    # Convert directory to a Path object if it exists
    if not directory or not Path(directory).exists():
        print(f"Directory not found for {id_prefix}")
        return [], pd.Timestamp.min, pd.Timestamp.min

    directory = Path(directory)  # Ensure directory is a Path object

    processed_data_cache = load_cache(id_prefix) or {}
    min_time, max_time = pd.Timestamp.max, pd.Timestamp.min
    available_days = set()
    cache_updated = False

    # List all .nc files, ignoring symbolic links and non-regular files
    nc_files = [f for f in directory.iterdir() if f.is_file() and f.suffix == '.nc' and f.name != f"{id_prefix}.nc"]

    if not nc_files:
        print(f"No .nc files found in {directory}")
        return [], pd.Timestamp.min, pd.Timestamp.min

    for file_path in nc_files:
        if not file_path.exists():
            print(f"File {file_path} not found. Skipping.")
            continue

        try:
            file_mtime = file_path.stat().st_mtime
            cache_entry = processed_data_cache.get(file_path.name, {})

            if (file_path.name in processed_data_cache and
                    isinstance(cache_entry, dict) and
                    cache_entry.get('mtime') == file_mtime and
                    all(key in cache_entry for key in ['min_time', 'max_time', 'available_days'])):

                file_min_time = cache_entry['min_time']
                file_max_time = cache_entry['max_time']
                file_available_days = cache_entry['available_days']

            else:
                file_min_time, file_max_time, file_available_days = process_file(file_path)
                if file_available_days:
                    processed_data_cache[file_path.name] = {
                        'mtime': file_mtime,
                        'min_time': file_min_time,
                        'max_time': file_max_time,
                        'available_days': file_available_days
                    }
                    cache_updated = True

            if file_available_days:
                min_time = min(min_time, file_min_time)
                max_time = max(max_time, file_max_time)
                available_days.update(file_available_days)

        except Exception as e:
            print(f"Error processing file {file_path.name}: {e}")
            continue

    if cache_updated:
        save_cache(processed_data_cache, id_prefix)

    disabled_days = []
    if min_time != pd.Timestamp.max and max_time != pd.Timestamp.min:
        all_days = set(pd.date_range(start=min_time, end=max_time).date)
        disabled_days = sorted(all_days - available_days)

    return disabled_days, min_time, max_time

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

