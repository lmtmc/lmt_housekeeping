from dash import Input, Output
from dash.exceptions import PreventUpdate
import base64
import io
import traceback
from toltec_files.cryocmp_file import ToltecCryocmpFile
from utils.plot_utils import update_plot

def cryocmp_register_callbacks(app):
    @app.callback(
            Output('cryocmp-plot', 'figure'),
            Input('upload-data-cryocmp', 'contents'),
            Input('hours-dropdown-cryocmp', 'value'),
            prevent_initial_call=True
        )
    def update_cryocmp_plot(contents, hours):
        if contents is None:
            raise PreventUpdate

        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            file_input = io.BytesIO(decoded)

            cryocmp_file = ToltecCryocmpFile(file_input)
            plot_data = cryocmp_file.getData(hours)
            if not plot_data:
                raise ValueError("No valid plot data available")
            fig = update_plot(plot_data, hours, options=None, split_value=None, watermark_labels=[])
            return fig

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())