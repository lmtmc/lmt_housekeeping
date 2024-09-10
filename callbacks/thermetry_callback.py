from dash import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import base64
import io
import dash_bootstrap_components as dbc
import traceback
from toltec_files.thermetry_file import ToltecThermetryFile
from utils.plot_utils import update_plot


def thermetry_register_callbacks(app):
    @app.callback(
        [Output('thermetry-plot', 'figure'),
         Output('invalid-channels-thermetry', 'children')],
        Input('upload-data-thermetry', 'contents'),
        Input('hours-dropdown-thermetry', 'value'),
        Input('plot-options-thermetry', 'value'),
        Input('split-value-thermetry', 'value'),
    )
    def update_thermetry_plot(contents, hours, options, split_value):
        if contents is None:
            raise PreventUpdate

        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            file_input = io.BytesIO(decoded)

            thermetry_file = ToltecThermetryFile(file_input)

            if not hasattr(thermetry_file, 'get_plot_data'):
                raise AttributeError("ToltecThermetryFile object does not have 'get_plot_data' method")

            plot_data, invalid_channels = thermetry_file.get_plot_data(hours)

            if not plot_data:
                raise ValueError("No valid plot data available")

            fig = update_plot(plot_data, hours, options, split_value, watermark_labels=['1.1_0.1_top'])

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




