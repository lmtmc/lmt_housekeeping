import dash_bootstrap_components as dbc
from dash import html
from layouts import basic_components as bc

def create_thermetry_layout():
    return dbc.Card([
        dbc.CardHeader([
            bc.title("Thermetry Dashboard"),
            dbc.Row([
                dbc.Col([
                    bc.time_range_dropdown('thermetry'),
                    bc.date_select('thermetry')
                ], width='auto'),
                dbc.Col(bc.plot_options('thermetry'), width='auto'),
                dbc.Col(bc.split_value('thermetry'), width='auto'),
                dbc.Col(bc.apply_button('thermetry'), width='auto')
            ],),
            html.Div(id='invalid-channels-thermetry', className='align-items-center mt-3 mb-3')
        ]),

        dbc.CardBody(bc.graph_component('thermetry'))
        ], style={'height': '90vh', 'overflow-y': 'auto'})  # Adds vertical space between rows for improved readability




