from datetime import timedelta

import pandas as pd

from data_files.base_file import ToltecBaseFile

import numpy as np
from functools import lru_cache

class ToltecDilutionFridgeFile(ToltecBaseFile):
    @lru_cache(maxsize=1)
    def _read_variables(self):
        self.df = pd.DataFrame()
        base_name = 'Data.ToltecDilutionFridge.'

        # Process 'time' column
        time_data = self.nc.variables[base_name + 'SampleTime'][:]
        self.df['time'] = pd.to_datetime(time_data, unit='s', utc=True)

        # Process 'Energized' column if available in nc variables
        if base_name + 'StsDevC1PtcSigState' in self.nc.variables:
            state_data = self.nc.variables[base_name + 'StsDevC1PtcSigState'][:]
            self.df['Energized'] = [
                10 if b''.join(state).decode().rstrip('\x00').strip() == 'ON' else 0
                for state in state_data
            ]
        else:
            self.df['Energized'] = np.nan  # Fallback in case data is missing

    def getData(self, data_selection, hours, start_date, end_date):

        if data_selection == 'Comp':
            data_keys = ['StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt', 'Energized']
        elif data_selection == 'Pump':
            data_keys = ['StsDevP1PresSigPres']
        elif data_selection == 'Temp':
            data_keys = [f'StsDevT{i}TempSigTemp' for i in range(1, 17)]
        elif data_selection == 'All':
            data_keys = [
                            'StsDevP1PresSigPres', 'StsDevP2PresSigPres', 'StsDevP3PresSigPres',
                            'StsDevP4PresSigPres', 'StsDevP5PresSigPres', 'StsDevP6PresSigPres',
                            'StsDevTurb1PumpSigPowr', 'StsDevTurb1PumpSigSpd',
                            'StsDevC1PtcSigWit', 'StsDevC1PtcSigWot', 'StsDevC1PtcSigOilt',
                            'StsDevC1PtcSigHt', 'StsDevC1PtcSigHlp', 'StsDevC1PtcSigHhp',
                            'StsDevH1HtrSigPowr', 'StsDevH2HtrSigPowr', 'StsDevH3HtrSigPowr','Energized'
                        ] + [f'StsDevT{i}TempSigTemp' for i in range(1, 17)] + [f'StsDevT{i}TempSigRes' for i in
                                                                                range(1, 17)]

        # Load variables into DataFrame only if they are in data_keys
        for var in data_keys:
            full_name = f'Data.ToltecDilutionFridge.{var}'
            if full_name in self.nc.variables:
                self.df[var] = self.nc.variables[full_name][:]


        # Filter the DataFrame by recent hours or start_date/end_date
        if hours > 0:
            recent_time = self.df['time'].iloc[-1] - timedelta(hours=hours)
            filtered_df = self.df[self.df['time'] >= recent_time]
        elif start_date and end_date:
            start_date = pd.to_datetime(start_date, utc=True)
            end_date = pd.to_datetime(end_date, utc=True)
            filtered_df = self.df[(self.df['time'] >= start_date) & (self.df['time'] <= end_date)]
        else:
            filtered_df = self.df

        # Label mapping for plot legend
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

        plot_data = [
            {
                'x': filtered_df['time'],
                'y': filtered_df[key],
                'name': label_mapping.get(key,key)
            }
            for key in data_keys if key in filtered_df.columns
]
        return plot_data

