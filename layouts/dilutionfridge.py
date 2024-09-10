import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objs as go

def create_dilutionFridge_layout():
    return html.Div([
        html.H3("Dilution Fridge Dashboard", className="text-center"),
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data-dilutionFridge',
                    children=html.Div(['Drag and Drop or ', html.A('Select File')]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                ),
                dbc.Row([
                    dbc.Col(dbc.Label("Select time range:")),
                    dbc.Col(dcc.Dropdown(
                        id='hours-dropdown-dilutionFridge',
                        options=[
                            {'label': 'All Data', 'value': 0},
                            {'label': '5 Hours', 'value': 5},
                            {'label': '24 Hours', 'value': 24},
                            {'label': '7 Days', 'value': 168}
                        ],
                        value=5
                    ))
                ]),
                dbc.Row([
                    dbc.Col(dbc.Label("Data Selections:")),
                    dbc.Col(dcc.Dropdown(options=[
                        {'label': 'All', 'value':'All'},
                        {'label': 'Comp', 'value': 'Comp'},
                        {'label': 'Pump', 'value': 'Pump'},
                        {'label': 'Temp', 'value': 'Temp'},
                    ],
                        id='data-selection-dilutionFridge',
                        value='Comp'))
                ]),
            ], width=3),
            dbc.Col([
                dcc.Loading(dcc.Graph(id='dilutionFridge-plot', figure=go.Figure()))
            ], width=9)
        ])
    ])