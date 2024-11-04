import pandas as pd
from data_files.base_file import ToltecBaseFile

class ToltecThermetryFile(ToltecBaseFile):
    def _read_variables(self):
        """Read and process thermetry data with optimized catching"""
        try:
            variables = self.nc.variables.keys()
            self.dataframes = {}

            # Process channel labels once
            self.chanLabels = self._get_channel_labels(variables)

            # Process all channels
            self._process_channels(variables)

        except Exception as e:
            print(f"Error in read_variables: {e}")
            self.dataframes = {label: pd.DataFrame() for label in self.chanLabels}

    def _get_channel_labels(self, variables):
        """Get channel labels with efficient processing"""
        try:
            if 'Header.ToltecThermetry.ChanLabel' in variables:
                nc_labels = self.nc.variables['Header.ToltecThermetry.ChanLabel'][:]
                decoded_labels = [b''.join(label).strip().decode() for label in nc_labels]
                return [f'Chan{i + 1} - {label}' for i, label in enumerate(decoded_labels)]

            return [f'Chan{i + 1}' for i in range(16)]

        except Exception as e:
            print(f"Error processing channel labels: {e}")
            return [f'Chan{i + 1}' for i in range(16)]

    def _process_channels(self, variables):
        """Process all channels efficiently"""
        for i in range(16):
            time_var = f'Data.ToltecThermetry.Time{i + 1}'
            temp_var = f'Data.ToltecThermetry.Temperature{i + 1}'

            if time_var not in variables or temp_var not in variables:
                print(f"Warning: Variables {time_var} or {temp_var} not found")
                self.dataframes[self.chanLabels[i]] = pd.DataFrame()
                continue

            try:
                df = self._create_channel_dataframe(time_var, temp_var)
                self.dataframes[self.chanLabels[i]] = df
            except Exception as e:
                print(f"Error processing channel {i + 1}: {e}")
                self.dataframes[self.chanLabels[i]] = pd.DataFrame()

    def _create_channel_dataframe(self, time_var, temp_var):
        """Create DataFrame for a single channel with optimized processing"""
        # Get data from netCDF
        time_data = self.nc.variables[time_var][:]
        temp_data = self.nc.variables[temp_var][:]

        # Filter invalid timestamps efficiently
        valid_mask = time_data > 0

        # Return empty DataFrame if no valid data
        if not valid_mask.any():
            return pd.DataFrame()

        # Create DataFrame only with valid data
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(time_data[valid_mask], unit='s'),
            'temperature': temp_data[valid_mask]
        })

        # Set index if we have valid data
        if not df.empty:
            df.set_index('timestamp', inplace=True)
        return df

    def get_max_min_time(self):
        """Get the maximum and minimum time for all channels"""
        max_time = pd.Timestamp.min
        min_time = pd.Timestamp.max

        for df in self.dataframes.values():
            if not df.empty:
                max_time = max(max_time, df.index.max())
                min_time = min(min_time, df.index.min())

        return min_time, max_time

    def get_plot_data(self, hours, start_date, end_date):
        """Get plot data with optimized time range filtering"""
        plot_data = []
        invalid_channels = []

        try:
            # Get valid dataframes efficiently
            valid_dfs = {label: df for label, df in self.dataframes.items() if not df.empty}

            if not valid_dfs:
                return [], list(self.dataframes.keys())

            # Calculate time range once
            time_range = self._calculate_time_range(valid_dfs, hours,start_date, end_date)
            if time_range is None:
                return [], list(self.dataframes.keys())

            start_time, end_time = time_range

            # Process each channel efficiently
            for channel_label, df in self.dataframes.items():
                if df.empty:
                    invalid_channels.append(channel_label)
                    continue

                # Use efficient boolean indexing
                filtered_data = df[start_time:end_time]

                if filtered_data.empty:
                    invalid_channels.append(channel_label)
                    continue

                plot_data.append({
                    'x': filtered_data.index,
                    'y': filtered_data['temperature'].values,
                    'name': channel_label
                })

        except Exception as e:
            print(f"Error in get_plot_data: {e}")
            return [], list(self.dataframes.keys())

        return plot_data, invalid_channels

    def _calculate_time_range(self, valid_dfs, hours, start_date, end_date):
        """Calculate time range for plotting efficiently"""
        try:
            if hours > 0:
                end_time = max(df.index.max() for df in valid_dfs.values())
                start_time = end_time - pd.Timedelta(hours=hours)
            else:
                start_time = pd.Timestamp(start_date)
                end_time = pd.Timestamp(end_date)
            return start_time, end_time
        except Exception as e:
            print(f"Error calculating time range: {e}")
            return None