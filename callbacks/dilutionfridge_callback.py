from dash import Input, Output
from dash.exceptions import PreventUpdate
import base64
import io
import traceback
from toltec_files.dilutionfridge_file import ToltecDilutionFridgeFile
from utils.plot_utils import update_plot


def dilutionfridge_register_callbacks(app):
    @app.callback(
            Output('dilutionFridge-plot', 'figure'),
            Input('upload-data-dilutionFridge', 'contents'),
            Input('hours-dropdown-dilutionFridge', 'value'),
            Input('data-selection-dilutionFridge', 'value'),
            prevent_initial_call=True
        )
    def update_dilutionFridge_plot(contents, hours, data_selection):
        if contents is None:
            raise PreventUpdate

        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            file_input = io.BytesIO(decoded)

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
            fig = update_plot(plot_data, hours, options=None, split_value=None, watermark_labels=[])
            return fig

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())