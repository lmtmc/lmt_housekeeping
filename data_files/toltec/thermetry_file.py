from data_files.base_file import ToltecBaseFile
import numpy as np
import datetime
from functools import lru_cache

class ToltecThermetryFile(ToltecBaseFile):
    @lru_cache(maxsize=1)
    def _read_variables(self):
        variables = self.nc.variables.keys()
        self.data['time'] = []
        self.data['temperature'] = []
        self.chanLabels = []

        for i in range(16):
            time_var = f'Data.ToltecThermetry.Time{i + 1}'
            temp_var = f'Data.ToltecThermetry.Temperature{i + 1}'
            if time_var in variables and temp_var in variables:
                self.data['time'].append(self.nc.variables[time_var][:])
                self.data['temperature'].append(self.nc.variables[temp_var][:])
            else:
                print(f"Warning: Variables {time_var} or {temp_var} not found in the netCDF file.")
                self.data['time'].append(np.array([]))
                self.data['temperature'].append(np.array([]))

        self.chanLabels = [f'Chan{i + 1}' for i in range(16)]
        if 'Header.ToltecThermetry.ChanLabel' in variables:
            try:
                nc_labels = self.nc.variables['Header.ToltecThermetry.ChanLabel'][:]
                self.chanLabels = [b''.join(label).strip().decode() for label in nc_labels]
            except Exception as e:
                print(f"Error reading channel labels: {e}")

    def get_plot_data(self, hours):
        plot_data = []
        invalid_channels = []

        if not self.data['time'] or not self.data['temperature']:
            return plot_data, invalid_channels

        try:
            if hours > 0:
                xmax = max(np.max(x.compressed()) for x in self.data['time'] if x.size > 0 and np.max(x.compressed()) > 0)
                xmin = xmax - hours * 3600
            else:
                xmin = min(np.min(x.compressed()) for x in self.data['time'] if x.size > 0 and np.min(x.compressed()) > 0)
                xmax = max(np.max(x.compressed()) for x in self.data['time'] if x.size > 0 and np.max(x.compressed()) > 0)
        except ValueError as e:
            print(f"Error calculating xmax or xmin: {e}")
            return plot_data, invalid_channels

        for i, (x, y) in enumerate(zip(self.data['time'], self.data['temperature'])):
            if x.size == 0 or y.size == 0 or not np.isfinite(y).any():
                invalid_channels.append(self.chanLabels[i])
                continue

            mask = (x >= xmin) & (x <= xmax)
            x_filtered = x[mask].compressed()
            y_filtered = y[mask].compressed()

            if len(x_filtered) == 0 or len(y_filtered) == 0:
                invalid_channels.append(self.chanLabels[i])
                continue

            try:
                dates = [datetime.datetime.utcfromtimestamp(ts) for ts in x_filtered]
                temp = y_filtered[-1]
                units = "mK" if abs(temp) < 0.5 else "K"
                temp_display = temp * 1000.0 if units == "mK" else temp
                label = f"{self.chanLabels[i]} ({temp_display:.2f} {units})"
                plot_data.append({"x": dates, "y": y_filtered, "name": label})
            except Exception as e:
                print(f"Error processing channel {i}: {e}")
                invalid_channels.append(self.chanLabels[i])

        return plot_data, invalid_channels
