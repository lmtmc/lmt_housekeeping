import os

import pandas as pd
import yaml
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
import traceback
from data_files.rsr.rsfend import RsFendFile
from utils.plot_utils import update_plot
from utils.data_utils import load_config, load_all_data, get_files

config_path = "./config.yaml"
config=load_config(config_path)

FIXED_DIRECTORY = config['fixed_directories']['rsfend']
_rsfend_cached_data = None
def rsfend_register_callbacks(app):
    @app.callback(
        [
            Output('rsfend-date-picker-range', 'style'),
        ],
        Input('hours-dropdown-rsfend', 'value'),
    )
    def update_rsfend_date_picker(hours):
        style = {'display': 'block'} if hours == 0 else {'display': 'none'}
        return style,

    @app.callback(
        [

            Output('rsfend-date-picker-range', 'disabled_days'),
            Output('rsfend-date-picker-range', 'start_date'),
            Output('rsfend-date-picker-range', 'end_date'),
            Output('rsfend-date-picker-range', 'min_date_allowed'),
            Output('rsfend-date-picker-range', 'max_date_allowed')
        ],
        [Input('hours-dropdown-rsfend', 'value'),]
    )
    def update_rsfend_date_picker(n):
        global _rsfend_cached_data

        if _rsfend_cached_data is None:
            disabled_dates, min_date, max_date = load_all_data('rsfend')
            _rsfend_cached_data = (disabled_dates, min_date, max_date)
        else:
            disabled_dates, min_date, max_date = _rsfend_cached_data
            # Ensure date objects for consistent comparison
        if isinstance(min_date, pd.Timestamp):
            min_date = min_date.date()
        if isinstance(max_date, pd.Timestamp):
            max_date = max_date.date()

        # Set start date to previous day or min_date if invalid
        previous_day = (pd.Timestamp(max_date) - pd.Timedelta(days=1)).date()
        start_date = max(min_date, previous_day)

        return disabled_dates, start_date, max_date, min_date, max_date

    @app.callback(
            Output('rsfend-plot', 'figure'),
            Input('rsfend-apply-btn', 'n_clicks'),
        [
            State('rsfend-date-picker-range', 'start_date'),
            State('rsfend-date-picker-range', 'end_date'),
            State('hours-dropdown-rsfend', 'value'),

        ]
        )
    def update_rsfend_plot(n, start_date, end_date, hours ):
        if n is None:
            raise PreventUpdate
        files = get_files('rsfend', hours, start_date, end_date)
        data = []

        try:
            for file in files:
                file_path = os.path.join(FIXED_DIRECTORY, file)
                rsfend_file = RsFendFile(file_path)
                plot_data = rsfend_file.getData(start_date, end_date, hours)

                if not plot_data:
                    print(f"Empty plot data for file: {file}")
                    continue
            data.extend(plot_data)
            fig = update_plot('Rsfend', plot_data, hours, options=None, split_value=None)
            return fig

        except Exception as e:
            error_message = f"Error processing file: {str(e)}"
            print(error_message)
            print(traceback.format_exc())
