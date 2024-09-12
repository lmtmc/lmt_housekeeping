from data_files.base_file import ToltecBaseFile
from utils.utils import get_data_and_labels, prepare_plot_data


class RsFendFile(ToltecBaseFile):
    BASE_NAME = 'Data.Rsfend.'
    DATA_KEYS = [
        'ColdPlateTemp', 'RotatorCDTemp', 'MmicAPrimaryTemp', '80KCharcoalPlateTemp',
        '20KCharcoalPlateTemp', 'SolenoidValveTemp', 'OpticsTemp', 'CompressorTemp']
    def _read_variables(self):
        try:
            for var in self.DATA_KEYS:
                full_var_name = self.BASE_NAME + var
                if full_var_name in self.nc.variables:
                    self.data[var] = self.nc.variables[full_var_name][:]
                else:
                    print(f"Variable {full_var_name} not found in the netCDF file.")
            self.data['time'] = self.nc.variables[f'{self.BASE_NAME}Time'][:]
        except Exception as e:
            print(f"Error reading rsfend variables: {e}")

    def getData(self, hours):
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

        xdata, ydata, labels = get_data_and_labels(self.data, self.DATA_KEYS, label_mapping)

        plot_data = prepare_plot_data(xdata, ydata, labels, hours)
        return plot_data