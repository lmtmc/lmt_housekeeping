import yaml
from dash import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import traceback
from toltec_files.thermetry_file import ToltecThermetryFile
from utils.plot_utils import update_plot
from utils.utils import get_options_from_folder

config_path = "./config.yaml"
with open(config_path, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

FIXED_DIRECTORY = config['fixed_directories']['thermetry']

# FIXED_DIRECTORY = "/home/lmt/data_lmt/thermetry"

def thermetry_register_callbacks(app):
    @app.callback(
        Output('thermetry-file-dropdown', 'options'),
        Input('url', 'pathname'),
    )
    def update_thermetry_file_list(pathname):
        # Get the list of files in the fixed directory
        options = get_options_from_folder(FIXED_DIRECTORY, 'thermetry')
        return options
    @app.callback(
        [Output('thermetry-plot', 'figure'),
         Output('invalid-channels-thermetry', 'children')],
        Input('thermetry-file-dropdown', 'value'),
        Input('hours-dropdown-thermetry', 'value'),
        Input('plot-options-thermetry', 'value'),
        Input('split-value-thermetry', 'value'),
    )
    def update_thermetry_plot(file_input, hours, options, split_value):
        if file_input is None:
            raise PreventUpdate
        try:
            # Read the file from the fixed directory
            thermetry_file = ToltecThermetryFile(file_input)

            if not hasattr(thermetry_file, 'get_plot_data'):
                raise AttributeError("ToltecThermetryFile object does not have 'get_plot_data' method")

            plot_data, invalid_channels = thermetry_file.get_plot_data(hours)

            if not plot_data:
                raise ValueError("No valid plot data available")

            fig = update_plot('Thermetry', plot_data, hours, options, split_value)

            invalid_channels_display = dbc.Alert(
                f"Invalid Channels: {', '.join(invalid_channels)}" if invalid_channels else "All channels valid",
                color="warning" if invalid_channels else "success"
            )

            return fig, invalid_channels_display

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())  # This will print the full traceback
            error_fig = go.Figure().add_annotation(text=error_message, showarrow=False, font=dict(size=20, color="red"))
            error_alert = dbc.Alert(error_message, color="danger")
            return error_fig, error_alert




