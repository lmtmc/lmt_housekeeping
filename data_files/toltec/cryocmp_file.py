from datetime import timedelta
import pandas as pd
from data_files.base_file import ToltecBaseFile

class ToltecCryocmpFile(ToltecBaseFile):
    def _read_variables(self):
        try:
            base_name = 'Data.ToltecCryocmp.'
            self.df = pd.DataFrame()
            for var in ['Time', 'CoolInTemp', 'CoolOutTemp', 'OilTemp', 'Energized']:
                full_name = base_name + var
                if full_name in self.nc.variables:
                    self.df[var] = self.nc.variables[full_name][:]
            # filter out NaN values
            self.df = self.df.dropna()
            # Set 'time' as datetime from 'Time' and multiply 'Energized' by 10
            self.df['time'] = pd.to_datetime(self.df['Time'], unit='s', utc=True, errors='coerce')
        except Exception as e:
            print(f"Error reading Cryocmp variables: {e}")

    def getData(self, start_date, end_date, hours):
        data_keys = ['CoolOutTemp', 'CoolInTemp', 'OilTemp', 'Energized']
        label_mapping = {
            'CoolOutTemp': 'Water Out Temp',
            'CoolInTemp': 'Water In Temp',
            'OilTemp': 'Oil Temp',
            'Energized': 'Energized'
        }

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

        # Convert temperatures to Fahrenheit
        for temp_var in ['CoolOutTemp', 'CoolInTemp', 'OilTemp']:
            if temp_var in filtered_df.columns:
                filtered_df.loc[:, temp_var] = filtered_df[temp_var] * 1.8 + 32

        # Multiply 'Energized' by 10
        filtered_df.loc[:, 'Energized'] = filtered_df['Energized'] * 10
        # Prepare data for plotting
        plot_data = [
            {
                'name': label_mapping.get(key, key),
                'x': filtered_df['time'],
                'y': filtered_df[key]
            }
            for key in data_keys if key in filtered_df.columns
        ]

        return plot_data