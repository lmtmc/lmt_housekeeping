import dash_bootstrap_components as dbc
from dash import dcc, html
from layouts import basic_components as bc

def create_cryocmp_layout():
    return dbc.Card(
        [
            dbc.CardHeader([
                bc.title("Cryocmp Dashboard"),
                html.Div(
                    dbc.Row([
                        dbc.Col([
                            bc.time_range_dropdown('cryocmp'),
                            bc.date_select('cryocmp')
                        ], width='auto'),
                        dbc.Col(bc.apply_button('cryocmp'), width='auto')]),
                ),
            ],),
            dbc.CardBody([

            bc.graph_component('cryocmp')
        ],),
    ],style={'height': '90vh', 'overflow-y': 'auto'})