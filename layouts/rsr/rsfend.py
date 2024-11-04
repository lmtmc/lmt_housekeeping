import dash_bootstrap_components as dbc
from dash import dcc, html
from layouts import basic_components as bc
def create_rsfend_layout():
    return dbc.Card([
        dbc.CardHeader([
            bc.title("RSR Dashboard"),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        bc.time_range_dropdown('rsfend'),
                        bc.date_select('rsfend')
                    ], width='auto'),
                    dbc.Col(bc.apply_button('rsfend'), width='auto')
                ])
            ])
        ]),
        dbc.CardBody(bc.graph_component('rsfend'))
    ],style={'height': '90vh', 'overflow-y': 'auto'})