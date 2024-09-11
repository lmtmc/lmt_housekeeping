import yaml
from dash import Input, Output
from dash.exceptions import PreventUpdate
import traceback
from toltec_files.dilutionfridge_file import ToltecDilutionFridgeFile
from utils.plot_utils import update_plot
from utils.utils import get_options_from_folder

config_path = "./config.yaml"
with open(config_path, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
FIXED_DIRECTORY = config['fixed_directories']['dilutionFridge']

def dilutionfridge_register_callbacks(app):
    @app.callback(
            Output('dilutionFridge-file-dropdown', 'options'),
            Input('url', 'pathname'),
        )
    def update_dilutionFridge_file_list(pathname):
        # Get the list of files in the fixed directory
        options = get_options_from_folder(FIXED_DIRECTORY, 'dilutionFridge')
        return options
    @app.callback(
            Output('dilutionFridge-plot', 'figure'),
            Input('dilutionFridge-file-dropdown', 'value'),
            Input('hours-dropdown-dilutionFridge', 'value'),
            Input('data-selection-dilutionFridge', 'value'),
            prevent_initial_call=True
        )
    def update_dilutionFridge_plot(file_input, hours, data_selection):
        if file_input is None:
            raise PreventUpdate

        try:
            dilutionFridge_file = ToltecDilutionFridgeFile(file_input)
            if data_selection == 'All':
                plot_data = dilutionFridge_file.getData(hours)
            elif data_selection == 'Comp':
                plot_data = dilutionFridge_file.get_comp_data(hours)
            elif data_selection == 'Pump':
                plot_data = dilutionFridge_file.get_pump_data(hours)
            elif data_selection == 'Temp':
                plot_data = dilutionFridge_file.get_temp_data(hours)
            else:
                raise ValueError(f"Invalid data selection: {data_selection}")
            if not plot_data:
                raise ValueError("No valid plot data available")
            fig = update_plot('Dilution Fridge', plot_data, hours, options=None, split_value=None)
            return fig

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())