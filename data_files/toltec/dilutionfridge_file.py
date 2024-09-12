from data_files.base_file import ToltecBaseFile
from utils.utils import get_data_and_labels, prepare_plot_data
import numpy as np
from functools import lru_cache

class ToltecDilutionFridgeFile(ToltecBaseFile):
    @lru_cache(maxsize=1)
    def _read_variables(self):
        base_name = 'Data.ToltecDilutionFridge.'
        variable_groups = {
            'DevP': [f'StsDevP{i}PresSigPres' for i in range(1, 7)],
            'DevTurb1Pump': ['StsDevTurb1PumpSigPowr', 'StsDevTurb1PumpSigSpd'],
            'DevC1Ptc': ['StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt', 'StsDevC1PtcSigHt',
                         'StsDevC1PtcSigHlp', 'StsDevC1PtcSigHhp', 'StsDevC1PtcSigState'],
            'DevHHtr': [f'StsDevH{i}HtrSigPowr' for i in range(1, 4)],
            'DevTTemp': [f'StsDevT{i}TempSigTemp' for i in range(1, 17)],
            'DevTRes': [f'StsDevT{i}TempSigRes' for i in range(1, 17)]
        }

        self.data['time'] = self.nc.variables[base_name + 'SampleTime'][:]

        for variables in variable_groups.values():
            for var in variables:
                full_name = base_name + var
                if full_name in self.nc.variables:
                    self.data[var] = self.nc.variables[full_name][:]

        if 'StsDevC1PtcSigState' in self.data:
            self.data['Energized'] = np.array([
                10 if b''.join(state).decode().rstrip('\x00').strip() == 'ON' else 0
                for state in self.data['StsDevC1PtcSigState']
            ])

    def getData(self, hours):
        data_keys = [
            'StsDevP1PresSigPres', 'StsDevP2PresSigPres', 'StsDevP3PresSigPres',
            'StsDevP4PresSigPres', 'StsDevP5PresSigPres', 'StsDevP6PresSigPres',
            'StsDevTurb1PumpSigPowr', 'StsDevTurb1PumpSigSpd',
            'StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt',
            'StsDevC1PtcSigHt', 'StsDevC1PtcSigHlp', 'StsDevC1PtcSigHhp',
            'StsDevH1HtrSigPowr', 'StsDevH2HtrSigPowr', 'StsDevH3HtrSigPowr'
        ] + [f'StsDevT{i}TempSigTemp' for i in range(1, 17)] + [f'StsDevT{i}TempSigRes' for i in range(1, 17)]

        label_mapping = {
            'StsDevP1PresSigPres': 'P1', 'StsDevP2PresSigPres': 'P2', 'StsDevP3PresSigPres': 'P3',
            'StsDevP4PresSigPres': 'P4', 'StsDevP5PresSigPres': 'P5', 'StsDevP6PresSigPres': 'P6',
            'StsDevTurb1PumpSigPowr': 'Power', 'StsDevTurb1PumpSigSpd': 'Speed',
            'StsDevC1PtcSigWit': 'H2O In Temp', 'StsDevC1PtcSigWot': 'H2O Out Temp',
            'StsDevC1PtcSigOilt': 'Oil Temp', 'StsDevC1PtcSigHt': 'Helium Temp',
            'StsDevC1PtcSigHlp': 'Low Pressure', 'StsDevC1PtcSigHhp': 'High Pressure',
            'StsDevH1HtrSigPowr': 'Chamber', 'StsDevH2HtrSigPowr': 'Still', 'StsDevH3HtrSigPowr': 'H3'
        }
        label_mapping.update({f'StsDevT{i}TempSigTemp': f'T{i}' for i in range(1, 17)})
        label_mapping.update({f'StsDevT{i}TempSigRes': f'R{i}' for i in range(1, 17)})

        xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)
        plot_data = prepare_plot_data(xdata, ydata, labels, hours)
        return plot_data

    def get_comp_data(self, hours):
        data_keys = ['StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt', 'Energized']
        label_mapping = {
            'StsDevC1PtcSigWit': 'Water In Temp',
            'StsDevC1PtcSigWot': 'Water Out Temp',
            'StsDevC1PtcSigOilt': 'Oil Temp',
            'Energized': 'Energized'
        }
        xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)

        for i in range(3):
            ydata[i] = ydata[i] * 1.8 + 32
        plot_data = prepare_plot_data(xdata, ydata, labels, hours)
        return plot_data

    def get_pump_data(self, hours):
        data_keys = ['StsDevP1PresSigPres']
        label_mapping = {'StsDevP1PresSigPres': 'P1'}
        xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)
        plot_data = prepare_plot_data(xdata, ydata, labels, hours)
        return plot_data

    def get_temp_data(self, hours):
        temp_keys = [key for key in self.data.keys() if 'TempSigTemp' in key]
        label_mapping = {}
        for key in temp_keys:
            v = self.nc.variables[f'Data.ToltecDilutionFridge.{key}']
            label = getattr(v, 'long_name', key)
            label_mapping[key] = f"{label} ({v[-1]:.2f} K)"
        xdata, ydata, labels = get_data_and_labels(self.data, temp_keys, label_mapping)
        plot_data = prepare_plot_data(xdata, ydata, labels, hours)
        return plot_data