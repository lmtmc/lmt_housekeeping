import dash_bootstrap_components as dbc
from dash import html
from layouts import basic_components as bc
def create_thermetry_layout():

    return html.Div([
        bc.title("Thermetry Dashboard"),
        dbc.Row([
            dbc.Col([
                bc.file_select('thermetry'),
                bc.time_range_dropdown('thermetry'),
                bc.plot_options('thermetry'),
                bc.split_value('thermetry'),
                html.Div(id='invalid-channels-thermetry', className='mt-3')
            ], width=3),
            dbc.Col([
                bc.graph_component('thermetry')
            ], width=9)
        ])
    ])



