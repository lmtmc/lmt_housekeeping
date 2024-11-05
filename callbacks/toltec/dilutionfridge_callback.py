import os

import pandas as pd
import yaml
from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from utils.data_utils import load_config
import traceback

from data_files.toltec.dilutionfridge_file import ToltecDilutionFridgeFile
from data_files.toltec.thermetry_file import ToltecThermetryFile
from utils.plot_utils import update_plot
from utils.data_utils import load_all_data, get_files

config_path = "./config.yaml"
_dilutionFridge_cached_data = None
config = load_config(config_path)
FIXED_DIRECTORY = config['fixed_directories']['dilutionFridge']

_dilutionfridge_cached_data = None
def dilutionfridge_register_callbacks(app):
    # if time range options is 0, show the custom range date picker
    @app.callback(
        [
            Output('dilutionFridge-date-picker-range', 'style'),
            Output('dilutionFridge-date-picker-range', 'disabled_days'),
            Output('dilutionFridge-date-picker-range', 'start_date'),
            Output('dilutionFridge-date-picker-range', 'end_date'),
            Output('dilutionFridge-date-picker-range', 'min_date_allowed'),
            Output('dilutionFridge-date-picker-range', 'max_date_allowed')
        ],
        [Input('hours-dropdown-dilutionFridge', 'value'),]
    )
    def update_dilutionfridge_date_picker(hours, _dilutionfridge_cached_data=None):

        # Control display style of date picker based on hours
        style = {'display': 'block'} if hours == 0 else {'display': 'none'}
        # Load data if not cached
        if _dilutionfridge_cached_data is None:
            disabled_dates, min_date, max_date = load_all_data('dilutionFridge')
            print('disabled_dates', len(disabled_dates), 'min_date', min_date, 'max_date', max_date)
            _dilutionfridge_cached_data = (disabled_dates, min_date, max_date)
        else:
            # Use cached data
            disabled_dates, min_date, max_date = _dilutionfridge_cached_data

        # Ensure date consistency
        if isinstance(min_date, pd.Timestamp):
            min_date = min_date.date()
        if isinstance(max_date, pd.Timestamp):
            max_date = max_date.date()

        # Set start date to previous day or min_date if invalid
        previous_day = (pd.Timestamp(max_date) - pd.Timedelta(days=1)).date()
        start_date = max(min_date, previous_day)

        return style, disabled_dates, start_date, max_date, min_date, max_date


    @app.callback(
    [
        Output('dilutionFridge-plot', 'figure'),
    ],
    Input('dilutionFridge-apply-btn', 'n_clicks'),
    [
        State('dilutionFridge-date-picker-range', 'start_date'),
        State('dilutionFridge-date-picker-range', 'end_date'),
        State('hours-dropdown-dilutionFridge', 'value'),
        State('data-selection-dilutionFridge', 'value'),
    ],
    )
    def update_dilutionFridge_plot(n, start_date, end_date, hours, data_selection):
        if n is None:
            raise PreventUpdate

        files = get_files('dilutionFridge', hours, start_date, end_date)
        data = []
        plot_data = []
        try:
            for file in files:
                file_path = os.path.join(FIXED_DIRECTORY, file)
                dilutionFridge_file = ToltecDilutionFridgeFile(file_path)
                plot_data = dilutionFridge_file.getData(data_selection, hours, start_date, end_date)
                data.extend(plot_data)

            fig = update_plot('Dilution Fridge', plot_data, hours, options=None, split_value=None)

            return [fig]

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())