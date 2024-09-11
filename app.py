import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from layouts.thermetry import create_thermetry_layout
from layouts.dilutionfridge import create_dilutionFridge_layout
from layouts.cryocmp import create_cryocmp_layout
from layouts.navbar import create_menu_bar
from callbacks.callbacks import register_callbacks
prefix = '/lmt_housekeeping'

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css",
    "https://use.fontawesome.com/releases/v5.15.3/css/all.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True,
                url_base_pathname=f'{prefix}/')
app.title = 'LMT Housekeeping Dashboard'

toltec_menu = create_menu_bar('TolTEC',
                              sub_nav_links=[
                                    {'label': 'Thermetry', 'href': f'{prefix}/thermetry'},
                                    {'label': 'Dilution Fridge', 'href': f'{prefix}/dilutionFridge'},
                                    {'label': 'Cryocmp', 'href': f'{prefix}/cryocmp'},
                              ],
                              main_id = 'toltec-dashboard-link',
                              icon_id = 'toltec-icon',
                              dropdown_id = 'toltec-dropdown')


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            toltec_menu,

        ], width=2),
        dbc.Col(html.Div(id="content"))
    ]),
    dcc.Location(id='url', refresh=False),
], fluid=True)

@app.callback(
    Output("content", "children"),
    Input("url", "pathname")
)
def render_content(pathname):
    if pathname == f'{prefix}/thermetry':
        return create_thermetry_layout()
    elif pathname == f'{prefix}/dilutionFridge':
        return create_dilutionFridge_layout()
    elif pathname == f'{prefix}/cryocmp':
        return create_cryocmp_layout()
    else:
        return create_thermetry_layout()  # Default to thermetry layout

@app.callback(
    Output('toltec-dropdown', 'style'),
    Output('toltec-icon', 'className'),
    Input('toltec-dashboard-link', 'n_clicks'),
    State('toltec-dropdown', 'style'),
    prevent_initial_call=True
)
def toggle_dropdown(n_clicks, dropdown_style):
    if n_clicks:
        is_open = dropdown_style['display'] == 'block'
        return (
            {'display': 'none' if is_open else 'block'},
            'bi bi-chevron-down' if is_open else 'bi bi-chevron-up'
        )
    return dropdown_style, 'bi bi-chevron-down'

@app.callback(
    [Output(f"{page}-link", "active") for page in ["thermetry", "dilutionFridge", "cryocmp"]],
    Input("url", "pathname")
)
def set_active_link(pathname):
    return [pathname == f"{prefix}/{page}" for page in ["thermetry", "dilutionFridge", "cryocmp"]]

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=False)