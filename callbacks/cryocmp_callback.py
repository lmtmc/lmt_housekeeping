import yaml
from dash import Input, Output
from dash.exceptions import PreventUpdate
import traceback
from toltec_files.cryocmp_file import ToltecCryocmpFile
from utils.plot_utils import update_plot
from utils.utils import  get_options_from_folder

config_path = "./config.yaml"
with open(config_path, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

FIXED_DIRECTORY = config['fixed_directories']['cryocmp']
def cryocmp_register_callbacks(app):
    @app.callback(
        Output('cryocmp-file-dropdown', 'options'),
        Input('url', 'pathname'),
    )
    def update_cryocmp_file_list(pathname):
        # Get the list of files in the fixed directory
        options = get_options_from_folder(FIXED_DIRECTORY, 'cryocmp')
        return options
    @app.callback(
            Output('cryocmp-plot', 'figure'),
            Input('cryocmp-file-dropdown', 'value'),
            Input('hours-dropdown-cryocmp', 'value'),
            prevent_initial_call=True
        )
    def update_cryocmp_plot(file_input, hours):
        if file_input is None:
            raise PreventUpdate

        try:
            cryocmp_file = ToltecCryocmpFile(file_input)
            plot_data = cryocmp_file.getData(hours)
            if not plot_data:
                raise ValueError("No valid plot data available")
            fig = update_plot(plot_data, hours, options=None, split_value=None)
            return fig

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())