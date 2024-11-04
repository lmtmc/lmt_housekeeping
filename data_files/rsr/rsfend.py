import pandas as pd

from data_files.base_file import ToltecBaseFile
from utils.data_utils import filter_dataframe_by_time


class RsFendFile(ToltecBaseFile):
    BASE_NAME = 'Data.Rsfend.'
    DATA_KEYS = [
        'ColdPlateTemp', 'RotatorCDTemp', 'MmicAPrimaryTemp', '80KCharcoalPlateTemp',
        '20KCharcoalPlateTemp', 'SolenoidValveTemp', 'OpticsTemp', 'CompressorTemp']
    def _read_variables(self):
        try:
            self.df = pd.DataFrame()
            for var in self.DATA_KEYS:
                full_var_name = self.BASE_NAME + var
                if full_var_name in self.nc.variables:
                    self.df[var] = self.nc.variables[full_var_name][:]
                else:
                    print(f"Variable {full_var_name} not found in the netCDF file.")
            self.df['time'] = pd.to_datetime(self.nc.variables[f'{self.BASE_NAME}Time'][:], unit='s', utc=True)
            self.df = self.df.dropna()
        except Exception as e:
            print(f"Error reading rsfend variables: {e}")

    def getData(self, start_data, end_date, hours):
        label_mapping = {
            'ColdPlateTemp': 'Cold Plate Temp',
            'RotatorCDTemp': 'Rotator CD Temp',
            'MmicAPrimaryTemp': 'Mmic A Primary Temp',
            '80KCharcoalPlateTemp': '80K Charcoal Plate Temp',
            '20KCharcoalPlateTemp': '20K Charcoal Plate Temp',
            'SolenoidValveTemp': 'Solenoid Valve Temp',
            'OpticsTemp': 'Optics Temp',
            'CompressorTemp': 'Compressor Temp'
        }

        # Filter the DataFrame by recent hours or start_date/end_date
        filtered_df = filter_dataframe_by_time(self.df, hours, start_data, end_date)

        plot_data = [
            {
                'name': label_mapping.get(key, key),
                'x': filtered_df['time'],
                'y': filtered_df[key]
            }
            for key in self.DATA_KEYS if key in filtered_df.columns
        ]
        return plot_data