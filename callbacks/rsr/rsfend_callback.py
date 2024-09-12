import yaml
from dash import Input, Output
from dash.exceptions import PreventUpdate
import traceback
from data_files.rsr.rsfend import RsFendFile
from utils.plot_utils import update_plot
from utils.utils import  get_options_from_folder

config_path = "./config.yaml"
with open(config_path, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

FIXED_DIRECTORY = config['fixed_directories']['rsfend']

def rsfend_register_callbacks(app):
    @app.callback(
        Output('rsfend-file-dropdown', 'options'),
        Input('url', 'pathname'),
    )
    def update_rsfend_file_list(pathname):
        # Get the list of files in the fixed directory
        options = get_options_from_folder(FIXED_DIRECTORY, 'rsfend')
        return options

    @app.callback(
        Output('rsfend-plot', 'figure'),
        Input('rsfend-file-dropdown', 'value'),
        Input('hours-dropdown-rsfend', 'value'),
        prevent_initial_call=True
    )
    def update_rsfend_plot(file_input, hours):
        if file_input is None:
            raise PreventUpdate

        try:
            rsfend_file = RsFendFile(file_input)
            plot_data = rsfend_file.getData(hours)
            if not plot_data:
                raise ValueError("No valid plot data available")
            fig = update_plot('Rsfend', plot_data, hours, options=None, split_value=None)
            return fig

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())