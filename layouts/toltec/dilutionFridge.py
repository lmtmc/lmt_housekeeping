import dash_bootstrap_components as dbc
from dash import dcc, html
from layouts import basic_components as bc
def create_dilutionFridge_layout():
    return html.Div([
        bc.title("Dilution Fridge Dashboard"),
        dbc.Row([
            dbc.Col([
                bc.file_select('dilutionFridge'),
                bc.time_range_dropdown('dilutionFridge'),
                dbc.Row([
                    dbc.Col(dbc.Label('Select Data:')),
                    dbc.Col(dcc.Dropdown(
                    id='data-selection-dilutionFridge',
                    options=[
                        {'label': 'All', 'value': 'all'},
                        {'label': 'Comp', 'value': 'Comp'},
                        {'label': 'Pump', 'value': 'Pump'},
                        {'label': 'Temp', 'value': 'Temp'}],
                    value='Comp'
                    ), )])
            ], width=3),
            dbc.Col([
                bc.graph_component('dilutionFridge')
            ], width=9)
        ])
    ])
