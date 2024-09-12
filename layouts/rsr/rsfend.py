import dash_bootstrap_components as dbc
from dash import dcc, html
from layouts import basic_components as bc
def create_rsfend_layout():
    return html.Div([
        bc.title("RSR Dashboard"),
        dbc.Row([
            dbc.Col([
                bc.file_select('rsfend'),
                bc.time_range_dropdown('rsfend'),
            ], width=3),
            dbc.Col([
                bc.graph_component('rsfend')
            ], width=9)
        ])
    ])