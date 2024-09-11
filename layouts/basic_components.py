from dash import html, dcc
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

def title(dashboard_title):
    return html.H5(dashboard_title)

def file_select(id_prefix):
    return dbc.Row([
        dbc.Col(
            html.Label(f"Select File (Start Date) ", className=" mb-4", ),
        ),
        dbc.Col(
            dcc.Dropdown(
                id=f'{id_prefix}-file-dropdown',
                options=[],
                placeholder="Select a file",
            )
        )
    ])

def time_range_dropdown(id_prefix):
    return dbc.Row([
        dbc.Col(html.Label("Select Time Range:", className="mb-4")),
        dbc.Col(dcc.Dropdown(
            id=f'hours-dropdown-{id_prefix}',
            options=[
                {'label': 'All Data', 'value': 0},
                {'label': '5 Hours', 'value': 5},
                {'label': '24 Hours', 'value': 24},
                {'label': '7 Days', 'value': 168}
            ],
            value=5
        ))
    ])

def plot_options(id_prefix):
    return dbc.Row([
        dbc.Col(html.Label("Plot Options:", className="mb-4")),
        dbc.Col(dcc.Checklist(
            id=f'plot-options-{id_prefix}',
            options=[
                {'label': 'Log Scale', 'value': 'log'},
            ]
        ))
    ])

def split_value(id_prefix):
    return dbc.Row([
        dbc.Col(html.Label("Split Value (K):", className=" mb-4")),
        dbc.Col(dcc.Input(
            id=f'split-value-{id_prefix}',
            type='number',
            placeholder='Enter a value',
        ))
    ])

def invalid_channels(id_prefix):
    return html.Div(id=f'invalid-channels-{id_prefix}', className='mt-3')

def graph_component(id_prefix):
    return dcc.Loading(dcc.Graph(id=f'{id_prefix}-plot', figure=go.Figure()))

