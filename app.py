# todo hold values for each page in a session store
# todo highlight active page in the menu

import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from layouts import menubar
from layouts.rsr import rsfend
from layouts.toltec import dilutionFridge, cryocmp, thermetry
from callbacks.callbacks import register_callbacks
import yaml

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
prefix = config['prefix']


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css",
    "https://use.fontawesome.com/releases/v5.15.3/css/all.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
                routes_pathname_prefix=f'{prefix}/', requests_pathname_prefix=f'{prefix}/',
                )
app.config.prevent_initial_callbacks = 'initial_duplicate'

app.title = 'LMT Housekeeping Dashboard'


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(menubar.create_menu_bar(),width=2),
        dbc.Col(html.Div(id="content"), width = 9)
    ]),
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='app-state', storage_type='session'),
], fluid=True)

def get_layout(pathname):
    if pathname == f'{prefix}/thermetry':
        return thermetry.create_thermetry_layout()
    elif pathname == f'{prefix}/dilutionFridge':
        return dilutionFridge.create_dilutionFridge_layout()
    elif pathname == f'{prefix}/cryocmp':
        return cryocmp.create_cryocmp_layout()
    elif pathname == f'{prefix}/rsfend':
        return rsfend.create_rsfend_layout()
    else:
        return thermetry.create_thermetry_layout()  # Default to thermetry layout
@app.callback(
    Output("content", "children"),
    Input("url", "pathname")
)
def render_content(pathname):
    return get_layout(pathname)

register_callbacks(app)

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)