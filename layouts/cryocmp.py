import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objs as go

def create_cryocmp_layout():
    return html.Div([
        html.H3("Cryocmp Dashboard", className="text-center"),
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data-cryocmp',
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
                        id='hours-dropdown-cryocmp',
                        options=[
                            {'label': 'All Data', 'value': 0},
                            {'label': '5 Hours', 'value': 5},
                            {'label': '24 Hours', 'value': 24},
                            {'label': '7 Days', 'value': 168}
                        ],
                        value=5
                    ))
                ]),
            ], width=3),
            dbc.Col([
                dcc.Loading(dcc.Graph(id='cryocmp-plot', figure=go.Figure()))
            ], width=9)
        ])
    ])