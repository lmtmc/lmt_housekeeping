from dash import html, dcc
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

def title(dashboard_title):
    return html.Div(html.H3(dashboard_title), className='mt-4 mb-4')

def file_select(id_prefix):
    return html.Div([
        dcc.Dropdown(
            id=f'{id_prefix}-file-dropdown',
            options=[],
            placeholder="Select a file",)
    ])

def date_select(id_prefix, min_date=None, max_date=None):
    return  html.Div(dbc.Row([
        # dbc.Col(html.Label("Select Date Range:", className="mb-4")),
        dbc.Col(dcc.DatePickerRange(
            id=f'{id_prefix}-date-picker-range',
            start_date=min_date,
            end_date=max_date,
            min_date_allowed=min_date,
            max_date_allowed=max_date,
            clearable=False
        ),width='auto'),
    ], className='mt-4 align-items-center'))

def time_range_dropdown(id_prefix):
    return dbc.Row([
        dbc.Col(dbc.Label("Select Time:", className='bold-label'), width='auto'),
        dbc.Col(dbc.RadioItems(
            id=f'hours-dropdown-{id_prefix}',
            options=[
                {'label': 'Last 5 hours', 'value': 5},
                {'label': 'Last 24 hours', 'value': 24},
                {'label': 'Custom Range', 'value': 0},
                # {'label': '7 Days', 'value': 168}
            ],
            inline=True,
            value=5
        ))
    ])

def apply_button(id_prefix):
    return dbc.Row([
        dbc.Col(dbc.Button('Apply', id=f'{id_prefix}-apply-btn', n_clicks=0), width='auto'),
    ], justify='end', className='ml-5')

def plot_options(id_prefix):
    return dbc.Row([
        dbc.Col(dbc.Label("Plot Options:", className='bold-label'),width='auto'),
        dbc.Col(dcc.Checklist(
            id=f'plot-options-{id_prefix}',
            options=[
                {'label': 'Log Scale', 'value': 'log'},
            ]
        ))
    ])

def split_value(id_prefix):
    return dbc.Row([
        dbc.Col(dbc.Label("Split Value (K):", className='bold-label')),
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

