from toltec_files.base_file import ToltecBaseFile
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
# import netCDF4
# import numpy as np
# import datetime
# import io
# import os
# from functools import lru_cache
#
# def filter_data_by_hours(xdata, ydata, hours):
#     print('xdata:', xdata)
#
#     try:
#         if hours > 0:
#             xmax = max(np.max(x) for x in xdata if x.size > 0 and np.max(x) > 0)
#             xmin = xmax - hours * 3600
#         else:
#             xmin = min(np.min(x) for x in xdata if x.size > 0 and np.min(x) > 0)
#             xmax = max(np.max(x) for x in xdata if x.size > 0 and np.max(x) > 0)
#     except ValueError as e:
#         print(f"Error calculating xmax or xmin: {e}")
#         return xdata, ydata
#
#     print(f"xmin: {xmin}, xmax: {xmax}")
#
#     mask = (xdata >= xmin) & (xdata <= xmax)
#     x_filtered = xdata[mask]
#     y_filtered = [y[mask] for y in ydata]
#
#     return x_filtered, y_filtered
#
#
# def prepare_plot_data(xdata, ydata, labels, hours):
#     xdata, ydata = filter_data_by_hours(xdata, ydata, hours)
#     x_datetime = [datetime.datetime.utcfromtimestamp(ts) for ts in xdata]
#     plot_data = [{'x': x_datetime, 'y': y.tolist(), 'name': label} for y, label in zip(ydata, labels)]
#     return plot_data
#
# def get_data_and_labels(data, data_keys, label_mapping):
#     print('data.keys' ,data.keys())
#
#     xdata = data.get('time', [])
#     ydata = []
#     labels = []
#     for key in data_keys:
#         if key in data:
#             ydata.append(data[key])
#             labels.append(label_mapping.get(key, key))
#     return xdata, ydata, labels
# class ToltecBaseFile:
#     def __init__(self, file_input):
#         self.nc = None
#         self.data = {}
#
#         if isinstance(file_input, str) and os.path.isfile(file_input):
#             self.nc = netCDF4.Dataset(file_input)
#         elif isinstance(file_input, io.BytesIO):
#             self.nc = netCDF4.Dataset('inmemory', memory=file_input.read())
#         else:
#             raise ValueError("Invalid file input. Must be a valid file path or a BytesIO object.")
#
#         self._read_variables()
#
#     def _read_variables(self):
#         raise NotImplementedError("Subclasses must implement this method")
#
#     def __del__(self):
#         if self.nc:
#             self.nc.close()
#
# class ToltecThermetryFile(ToltecBaseFile):
#     @lru_cache(maxsize=1)
#     def _read_variables(self):
#         variables = self.nc.variables.keys()
#         self.data['time'] = []
#         self.data['temperature'] = []
#         self.chanLabels = []
#
#         for i in range(16):
#             time_var = f'Data.ToltecThermetry.Time{i + 1}'
#             temp_var = f'Data.ToltecThermetry.Temperature{i + 1}'
#             if time_var in variables and temp_var in variables:
#                 self.data['time'].append(self.nc.variables[time_var][:])
#                 self.data['temperature'].append(self.nc.variables[temp_var][:])
#             else:
#                 print(f"Warning: Variables {time_var} or {temp_var} not found in the netCDF file.")
#                 self.data['time'].append(np.array([]))
#                 self.data['temperature'].append(np.array([]))
#
#         self.chanLabels = [f'Chan{i + 1}' for i in range(16)]
#         if 'Header.ToltecThermetry.ChanLabel' in variables:
#             try:
#                 nc_labels = self.nc.variables['Header.ToltecThermetry.ChanLabel'][:]
#                 self.chanLabels = [b''.join(label).strip().decode() for label in nc_labels]
#             except Exception as e:
#                 print(f"Error reading channel labels: {e}")
#
#     def get_plot_data(self, hours):
#         plot_data = []
#         invalid_channels = []
#
#         if not self.data['time'] or not self.data['temperature']:
#             return plot_data, invalid_channels
#
#         try:
#             if hours > 0:
#                 xmax = max(np.max(x.compressed()) for x in self.data['time'] if x.size > 0 and np.max(x.compressed()) > 0)
#                 xmin = xmax - hours * 3600
#             else:
#                 xmin = min(np.min(x.compressed()) for x in self.data['time'] if x.size > 0 and np.min(x.compressed()) > 0)
#                 xmax = max(np.max(x.compressed()) for x in self.data['time'] if x.size > 0 and np.max(x.compressed()) > 0)
#         except ValueError as e:
#             print(f"Error calculating xmax or xmin: {e}")
#             return plot_data, invalid_channels
#
#         for i, (x, y) in enumerate(zip(self.data['time'], self.data['temperature'])):
#             if x.size == 0 or y.size == 0 or not np.isfinite(y).any():
#                 invalid_channels.append(self.chanLabels[i])
#                 continue
#
#             mask = (x >= xmin) & (x <= xmax)
#             x_filtered = x[mask].compressed()
#             y_filtered = y[mask].compressed()
#
#             if len(x_filtered) == 0 or len(y_filtered) == 0:
#                 invalid_channels.append(self.chanLabels[i])
#                 continue
#
#             try:
#                 dates = [datetime.datetime.utcfromtimestamp(ts) for ts in x_filtered]
#                 temp = y_filtered[-1]
#                 units = "mK" if abs(temp) < 0.5 else "K"
#                 temp_display = temp * 1000.0 if units == "mK" else temp
#                 label = f"{self.chanLabels[i]} ({temp_display:.2f} {units})"
#                 plot_data.append({"x": dates, "y": y_filtered, "name": label})
#             except Exception as e:
#                 print(f"Error processing channel {i}: {e}")
#                 invalid_channels.append(self.chanLabels[i])
#
#         return plot_data, invalid_channels
#
# class ToltecDilutionFridgeFile(ToltecBaseFile):
#     @lru_cache(maxsize=1)
#     def _read_variables(self):
#         base_name = 'Data.ToltecDilutionFridge.'
#         variable_groups = {
#             'DevP': [f'StsDevP{i}PresSigPres' for i in range(1, 7)],
#             'DevTurb1Pump': ['StsDevTurb1PumpSigPowr', 'StsDevTurb1PumpSigSpd'],
#             'DevC1Ptc': ['StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt', 'StsDevC1PtcSigHt',
#                          'StsDevC1PtcSigHlp', 'StsDevC1PtcSigHhp', 'StsDevC1PtcSigState'],
#             'DevHHtr': [f'StsDevH{i}HtrSigPowr' for i in range(1, 4)],
#             'DevTTemp': [f'StsDevT{i}TempSigTemp' for i in range(1, 17)],
#             'DevTRes': [f'StsDevT{i}TempSigRes' for i in range(1, 17)]
#         }
#
#         self.data['time'] = self.nc.variables[base_name + 'SampleTime'][:]
#
#         for variables in variable_groups.values():
#             for var in variables:
#                 full_name = base_name + var
#                 if full_name in self.nc.variables:
#                     self.data[var] = self.nc.variables[full_name][:]
#
#         if 'StsDevC1PtcSigState' in self.data:
#             self.data['Energized'] = np.array([
#                 10 if b''.join(state).decode().rstrip('\x00').strip() == 'ON' else 0
#                 for state in self.data['StsDevC1PtcSigState']
#             ])
#
#     def getData(self, hours):
#         data_keys = [
#             'StsDevP1PresSigPres', 'StsDevP2PresSigPres', 'StsDevP3PresSigPres',
#             'StsDevP4PresSigPres', 'StsDevP5PresSigPres', 'StsDevP6PresSigPres',
#             'StsDevTurb1PumpSigPowr', 'StsDevTurb1PumpSigSpd',
#             'StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt',
#             'StsDevC1PtcSigHt', 'StsDevC1PtcSigHlp', 'StsDevC1PtcSigHhp',
#             'StsDevH1HtrSigPowr', 'StsDevH2HtrSigPowr', 'StsDevH3HtrSigPowr'
#         ] + [f'StsDevT{i}TempSigTemp' for i in range(1, 17)] + [f'StsDevT{i}TempSigRes' for i in range(1, 17)]
#
#         label_mapping = {
#             'StsDevP1PresSigPres': 'P1', 'StsDevP2PresSigPres': 'P2', 'StsDevP3PresSigPres': 'P3',
#             'StsDevP4PresSigPres': 'P4', 'StsDevP5PresSigPres': 'P5', 'StsDevP6PresSigPres': 'P6',
#             'StsDevTurb1PumpSigPowr': 'Power', 'StsDevTurb1PumpSigSpd': 'Speed',
#             'StsDevC1PtcSigWit': 'H2O In Temp', 'StsDevC1PtcSigWot': 'H2O Out Temp',
#             'StsDevC1PtcSigOilt': 'Oil Temp', 'StsDevC1PtcSigHt': 'Helium Temp',
#             'StsDevC1PtcSigHlp': 'Low Pressure', 'StsDevC1PtcSigHhp': 'High Pressure',
#             'StsDevH1HtrSigPowr': 'Chamber', 'StsDevH2HtrSigPowr': 'Still', 'StsDevH3HtrSigPowr': 'H3'
#         }
#         label_mapping.update({f'StsDevT{i}TempSigTemp': f'T{i}' for i in range(1, 17)})
#         label_mapping.update({f'StsDevT{i}TempSigRes': f'R{i}' for i in range(1, 17)})
#
#         xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)
#         plot_data = prepare_plot_data(xdata, ydata, labels, hours)
#         return plot_data
#
#     def get_comp_data(self, hours):
#         data_keys = ['StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt', 'Energized']
#         label_mapping = {
#             'StsDevC1PtcSigWit': 'Water In Temp',
#             'StsDevC1PtcSigWot': 'Water Out Temp',
#             'StsDevC1PtcSigOilt': 'Oil Temp',
#             'Energized': 'Energized'
#         }
#         xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)
#
#         for i in range(3):
#             ydata[i] = ydata[i] * 1.8 + 32
#         plot_data = prepare_plot_data(xdata, ydata, labels, hours)
#         return plot_data
#
#     def get_pump_data(self, hours):
#         data_keys = ['StsDevP1PresSigPres']
#         label_mapping = {'StsDevP1PresSigPres': 'P1'}
#         xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)
#         plot_data = prepare_plot_data(xdata, ydata, labels, hours)
#         return plot_data
#
#     def get_temp_data(self, hours):
#         temp_keys = [key for key in self.data.keys() if 'TempSigTemp' in key]
#         label_mapping = {}
#         for key in temp_keys:
#             v = self.nc.variables[f'Data.ToltecDilutionFridge.{key}']
#             label = getattr(v, 'long_name', key)
#             label_mapping[key] = f"{label} ({v[-1]:.2f} K)"
#         xdata, ydata, labels = get_data_and_labels(self.data, temp_keys, label_mapping)
#         plot_data = prepare_plot_data(xdata, ydata, labels, hours)
#         return plot_data
#
# class ToltecCryocmpFile(ToltecBaseFile):
#     def _read_variables(self):
#         try:
#             base_name = 'Data.ToltecCryocmp.'
#             print('self.nc variables',self.nc.variables.keys())
#             for var in ['Time', 'CoolInTemp', 'CoolOutTemp', 'OilTemp', 'Energized']:
#                 self.data[var] = self.nc.variables[base_name + var][:]
#             self.data['time'] = self.data['Time']
#             self.data['Energized'] *= 10
#         except Exception as e:
#             print(f"Error reading Cryocmp variables: {e}")
#
#     def getData(self, hours):
#         data_keys = ['CoolOutTemp', 'CoolInTemp', 'OilTemp', 'Energized']
#         label_mapping = {
#             'CoolOutTemp': 'Water Out Temp',
#             'CoolInTemp': 'Water In Temp',
#             'OilTemp': 'Oil Temp',
#             'Energized': 'Energized'
#         }
#
#         xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)
#
#         # Convert to Fahrenheit
#         for i in range(3):
#             ydata[i] = ydata[i] * 1.8 + 32
#
#         plot_data = prepare_plot_data(xdata, ydata, labels, hours)
#         return plot_data
