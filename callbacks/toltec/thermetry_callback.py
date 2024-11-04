import os

import pandas as pd
import yaml
from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import traceback
from data_files.toltec.thermetry_file import ToltecThermetryFile
from utils.plot_utils import update_plot
from utils.data_utils import load_all_data, get_files, load_config

config_path = "./config.yaml"
config = load_config(config_path)

FIXED_DIRECTORY = config['fixed_directories']['thermetry']

_thermetry_cached_data = None
def thermetry_register_callbacks(app):
    # if time range options is 0, show the custom range date picker
    @app.callback(
        [
            Output('thermetry-date-picker-range', 'style'),
            Output('thermetry-date-picker-range', 'disabled_days'),
            Output('thermetry-date-picker-range', 'start_date'),
            Output('thermetry-date-picker-range', 'end_date'),
            Output('thermetry-date-picker-range', 'min_date_allowed'),
            Output('thermetry-date-picker-range', 'max_date_allowed')
        ],
        [Input('hours-dropdown-thermetry', 'value'),]
    )
    def update_thermetry_date_picker(hours):
        global _thermetry_cached_data

        # Part 1: Show or hide the date picker based on hours
        style = {'display': 'block'} if hours == 0 else {'display': 'none'}

        # Part 2: Set disabled days and date range based on data
        if _thermetry_cached_data is None:
            disabled_dates, min_date, max_date = load_all_data('thermetry')
            _thermetry_cached_data = (disabled_dates, min_date, max_date)
        else:
            disabled_dates, min_date, max_date = _thermetry_cached_data

        # Ensure date objects for consistent comparison
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
            Output('thermetry-plot', 'figure'),
            Output('invalid-channels-thermetry', 'children')
        ],
        Input('thermetry-apply-btn', 'n_clicks'),
        [
            State('thermetry-date-picker-range', 'start_date'),
            State('thermetry-date-picker-range', 'end_date'),
            State('hours-dropdown-thermetry', 'value'),
            State('plot-options-thermetry', 'value'),
            State('split-value-thermetry', 'value'),],
    )
    def update_thermetry_plot(n, start_date, end_date, hours, options, split_value):
        if n is None:
            raise PreventUpdate
        files = get_files('thermetry', hours, start_date, end_date)
        data = []
        potentially_invalid_channels = set()  # Start by assuming all channels might be invalid
        verified_valid_channels = set()  # Track channels that are valid in at least one file

        try:
            for file in files:
                # Read the file from the fixed directory
                file_path = os.path.join(FIXED_DIRECTORY, file)
                thermetry_file = ToltecThermetryFile(file_path)

                if not hasattr(thermetry_file, 'get_plot_data'):
                    raise AttributeError("ToltecThermetryFile object does not have 'get_plot_data' method")

                # Get plot data and invalid channels for the current file
                file_plot_data, file_invalid_channels = thermetry_file.get_plot_data(hours, start_date, end_date)

                if not file_plot_data:
                    print(f"No valid plot data available for file: {file}")
                    continue

                # Accumulate plot data
                data.extend(file_plot_data)

                # Track channels that were invalid in this file
                potentially_invalid_channels.update(file_invalid_channels)

                # Track channels that are valid in this file, removing them from potentially invalid channels
                valid_channels_in_file = set(df['name'] for df in file_plot_data)
                verified_valid_channels.update(valid_channels_in_file)
                potentially_invalid_channels.difference_update(valid_channels_in_file)

            # Generate the plot with accumulated data
            fig = update_plot('Thermetry', data, hours, options, split_value)

            # Display only channels that are invalid across all files
            final_invalid_channels = potentially_invalid_channels - verified_valid_channels
            invalid_channels_display = dbc.Alert(
                f"Invalid Channels: {', '.join(final_invalid_channels)}",
                color="warning" if final_invalid_channels else "success"
            ) if final_invalid_channels else None

            return fig, invalid_channels_display

        except Exception as e:
            error_message = f"Error processing files: {str(e)}"
            print(error_message)
            print(traceback.format_exc())  # This will print the full traceback
            error_fig = go.Figure().add_annotation(text=error_message, showarrow=False, font=dict(size=20, color="red"))
            error_alert = dbc.Alert(error_message, color="danger")
            return error_fig, error_alert