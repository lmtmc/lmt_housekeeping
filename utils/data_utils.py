import time
from datetime import date
from pathlib import Path
import os
import pandas as pd
import yaml
import xarray as xr
import pickle
config_path = "./config.yaml"

thermetry_invalid_files = [
    'thermetry_2022-05-04_000001_00_1651679215.nc'
    'thermetry_2022-06-21_000001_00_1655834695.nc',
    'thermetry_2022-06-21_000001_00_1655834156.nc',
    'thermetry_2022-06-16_000001_00_1655338606.nc',
    'thermetry_2022-05-27_000001_00_1653674485.nc',
    'thermetry_2020-12-28_000001_00_1609188730.nc',
    'thermetry_2019-10-31_000001_00_1572550678.nc',
    'thermetry_2019-03-25_000001_00_1553536659.nc',
]
def load_config(config_path):
    try:
        with open(config_path, 'r') as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        return None

# config = load_config(config_path)
# fixed_directories = config['fixed_directories']
fixed_directories = {'thermetry': '/home/lmt/data_lmt/thermetry', 'dilutionFridge': '/home/lmt/data_lmt/dilutionFridge', 'cryocmp': '/home/lmt/data_lmt/cryocmp', 'rsfend': '/home/lmt/data_lmt/rsfend'}
def filter_dataframe_by_time(df, hours=0, start_date=None, end_date=None):
    """
    Filters a DataFrame by the most recent hours or a specified date range.

    Parameters:
    - df (pd.DataFrame): The DataFrame to filter, with a 'time' column in datetime format.
    - hours (int): Number of recent hours to filter by. Overrides start_date and end_date if > 0.
    - start_date (str or pd.Timestamp): The start date to filter from (inclusive).
    - end_date (str or pd.Timestamp): The end date to filter up to (inclusive).

    Returns:
    - filtered_df (pd.DataFrame): The filtered DataFrame.
    """
    df['time'] = pd.to_datetime(df['time'], utc=True)

    if hours > 0:
        recent_time = df['time'].iloc[-1] - pd.Timedelta(hours=hours)
        return df[df['time'] >= recent_time]

    if start_date and end_date:
        start_date = pd.to_datetime(start_date, utc=True)
        end_date = pd.to_datetime(end_date, utc=True)
        return df[(df['time'] >= start_date) & (df['time'] <= end_date)]

    return df

def load_cache(id_prefix):
    """Load processed data cache from disk, or create a new one if not available."""
    cache_file_path = Path(f'./cache/{id_prefix}.pkl')

    if cache_file_path.exists() and os.path.getsize(cache_file_path) > 0:
        try:
            with open(cache_file_path, 'rb') as f:
                return pickle.load(f)
        except EOFError:
            print(f"Warning: Cache file {cache_file_path} is empty or corrupted. Recreating the cache.")

    print(f"No cache found at {cache_file_path} or cache is empty. Recreating cache.")
    return {}

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
    Returns:
        tuple: (disabled_days, min_time, max_time)
    """
    directory = fixed_directories.get(id_prefix)
    if not directory or not Path(directory).exists():
        print(f"Directory not found for {id_prefix}")
        return [], date.today(), date.today()  # Return today's date instead of None

    processed_data_cache = load_cache(id_prefix)
    min_time = pd.Timestamp.max.tz_localize(None)
    max_time = pd.Timestamp.min.tz_localize(None)
    available_days = set()
    cache_updated = False

    nc_files = [f for f in Path(directory).glob('*.nc')
                if f.is_file() and f.name != f'{id_prefix}.nc']

    if not nc_files:
        print(f"No .nc files found in {directory}")
        return [], date.today(), date.today()  # Return today's date instead of None

    valid_data_found = False

    for file_path in nc_files:
        if not file_path.exists():
            continue

        try:
            file_mtime = file_path.stat().st_mtime
            cache_entry = processed_data_cache.get(file_path.name)

            if cache_entry:
                file_min_time = pd.Timestamp(cache_entry['min_time'])
                file_max_time = pd.Timestamp(cache_entry['max_time'])
                file_available_days = cache_entry['available_days']
                #print(f"Loaded {file_path.name} from cache", file_min_time, file_max_time,len(file_available_days))
            else:
                file_min_time, file_max_time, file_available_days = process_file(str(file_path))

                if file_min_time is not None and file_max_time is not None:
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
                valid_data_found = True

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue

    if cache_updated:
        save_cache(processed_data_cache, id_prefix)

    if not valid_data_found:
        return [], date.today(), date.today()  # Return today's date instead of None

    disabled_days = []
    if min_time != pd.Timestamp.max and max_time != pd.Timestamp.min:
        all_days = set(pd.date_range(start=min_time, end=max_time).date)
        disabled_days = sorted(all_days - available_days)

    # Convert to date objects for consistency
    min_time = min_time.date()
    max_time = max_time.date()

    return disabled_days, min_time, max_time


def process_file(file_path):
    """Process an individual .nc file to extract min_time, max_time, and available days."""
    min_time, max_time = None, None
    available_days = set()

    try:
        # Extract the date from filename (assuming format: thermetry_YYYY-MM-DD_...)
        file_date_str = os.path.basename(file_path).split('_')[1]
        file_date = pd.to_datetime(file_date_str)  # Convert to Timestamp instead of date

        # Allow data range
        valid_start = file_date
        valid_end = file_date + pd.Timedelta(days=365)

        with xr.open_dataset(file_path) as ds:
            if 'thermetry_' in file_path and os.path.basename(file_path) not in thermetry_invalid_files:
                min_time, max_time, available_days = _process_data(
                    ds, 'Data.ToltecThermetry.Time', 16,
                    valid_start=valid_start,
                    valid_end=valid_end,
                    file_path=file_path  # Pass file_path for better error messages
                )
            elif 'dilutionFridge_' in file_path:
                min_time, max_time, available_days = _process_data(
                    ds, 'Data.ToltecDilutionFridge.SampleTime',
                    valid_start=valid_start,
                    valid_end=valid_end,
                    file_path=file_path
                )
            elif 'cryocmp_' in file_path:
                min_time, max_time, available_days = _process_data(
                    ds, 'Data.ToltecCryocmp.Time',
                    valid_start=valid_start,
                    valid_end=valid_end,
                    file_path=file_path
                )
            elif 'rsfend_' in file_path:
                min_time, max_time, available_days = _process_data(
                    ds, 'Data.Rsfend.Time',
                    valid_start=valid_start,
                    valid_end=valid_end,
                    file_path=file_path
                )
            else:
                print(f"Invalid File: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    return min_time, max_time, available_days


def _process_data(ds, time_var_base, num_channels=1, valid_start=None, valid_end=None, file_path=None):
    """Generalized function to process data and extract min_time, max_time, and available days."""
    min_time, max_time = pd.Timestamp.max, pd.Timestamp.min
    available_days = set()

    for i in range(1, num_channels + 1):
        time_var = f'{time_var_base}{i}' if num_channels > 1 else time_var_base
        if time_var in ds.variables:
            time_data = ds[time_var].values

            # Print raw time range for debugging
            if len(time_data) > 0:
                print(f"Channel {i} raw time range: {time_data.min()} to {time_data.max()}")

            time_data = time_data[time_data > 0]  # Filter non-positive times

            if len(time_data) == 0:
                continue

            # Convert to datetime
            timestamps = pd.to_datetime(time_data, unit='s')

            # Filter timestamps within valid range
            if valid_start and valid_end:
                # Convert timestamps to tz-naive if they're tz-aware
                if timestamps.tz is not None:
                    timestamps = timestamps.tz_localize(None)

                mask = (timestamps >= valid_start) & (timestamps <= valid_end)
                valid_timestamps = timestamps[mask]

                if len(valid_timestamps) == 0:
                    print(f"Warning: All timestamps in {file_path} channel {i} were outside valid range")
                    print(f"Time range: {timestamps.min()} to {timestamps.max()}")
                    print(f"Valid range: {valid_start} to {valid_end}")
                    continue

                timestamps = valid_timestamps

            min_time = min(min_time, timestamps.min())
            max_time = max(max_time, timestamps.max())
            available_days.update(timestamps.normalize().date)

    if min_time == pd.Timestamp.max or max_time == pd.Timestamp.min:
        return None, None, set()

    return min_time, max_time, available_days


# if start_date == end_date get all the files that contain the start_date
# if start_date != end_date get all the files that has available date between the start_date and end_date
# return a list containing the file names
def get_files(id_prefix, hours, start_date, end_date):
    # Load existing cache (if any)
    processed_data_cache = load_cache(id_prefix) or {}
    # if hours is 0 then the start_date and end_date are dates from the date picker, else date is more max_time
    if hours == 0:
        start_date = pd.Timestamp(start_date).date()
        end_date = pd.Timestamp(end_date).date()
    else:
        # get the data in the last file that was processed
        print("Getting last file", id_prefix,load_all_data(id_prefix)[2])
        end_date = load_all_data(id_prefix)[2]
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