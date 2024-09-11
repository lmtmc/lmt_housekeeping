from toltec_files.base_file import ToltecBaseFile
from utils.utils import get_data_and_labels, prepare_plot_data
class ToltecCryocmpFile(ToltecBaseFile):
    def _read_variables(self):
        try:
            base_name = 'Data.ToltecCryocmp.'
            for var in ['Time', 'CoolInTemp', 'CoolOutTemp', 'OilTemp', 'Energized']:
                self.data[var] = self.nc.variables[base_name + var][:]
            self.data['time'] = self.data['Time']
            self.data['Energized'] *= 10
        except Exception as e:
            print(f"Error reading Cryocmp variables: {e}")

    def getData(self, hours):
        data_keys = ['CoolOutTemp', 'CoolInTemp', 'OilTemp', 'Energized']
        label_mapping = {
            'CoolOutTemp': 'Water Out Temp',
            'CoolInTemp': 'Water In Temp',
            'OilTemp': 'Oil Temp',
            'Energized': 'Energized'
        }

        xdata, ydata, labels = get_data_and_labels(self.data, data_keys, label_mapping)
        # print('len(xdata)', len(xdata))
        # print('len(ydata)', len(ydata))
        # Convert to Fahrenheit
        for i in range(3):
            ydata[i] = ydata[i] * 1.8 + 32

        plot_data = prepare_plot_data(xdata, ydata, labels, hours)
        return plot_data