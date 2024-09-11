import dash_bootstrap_components as dbc
from dash import dcc, html
from layouts import basic_components as bc
def create_cryocmp_layout():
    return html.Div([
        bc.title("Cryocmp Dashboard"),
        dbc.Row([
            dbc.Col([
                bc.file_select('cryocmp'),
                bc.time_range_dropdown('cryocmp'),
            ], width=3),
            dbc.Col([
                bc.graph_component('cryocmp')
            ], width=9)
        ])
    ])