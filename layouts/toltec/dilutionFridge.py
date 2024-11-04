import dash_bootstrap_components as dbc
from dash import dcc, html
from layouts import basic_components as bc


def create_dilutionFridge_layout():
    # Define options for the data selection RadioItems to avoid repetition
    data_selection_options = [
        {'label': 'All', 'value': 'all'},
        {'label': 'Comp', 'value': 'Comp'},
        {'label': 'Pump', 'value': 'Pump'},
        {'label': 'Temp', 'value': 'Temp'}
    ]

    return dbc.Card([
        dbc.CardHeader([
            bc.title("Dilution Fridge Dashboard"),
            dbc.Row([
                dbc.Col([
                    bc.time_range_dropdown('dilutionFridge'),
                    bc.date_select('dilutionFridge')
                ], width='auto'),

                dbc.Col(html.H5('Select Data:'), width='auto'),

                dbc.Col(
                    dbc.RadioItems(
                        id='data-selection-dilutionFridge',
                        options=data_selection_options,
                        value='Comp', inline=True
                    ), width='auto'
                ),

                dbc.Col(bc.apply_button('dilutionFridge'))
            ])
        ]),

        dbc.CardBody(bc.graph_component('dilutionFridge'))
    ],style={'height': '90vh', 'overflow-y': 'auto'})
