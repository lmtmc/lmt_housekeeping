import dash
from dash import html, Output, Input, ctx
import dash_bootstrap_components as dbc
from layouts.thermetry import create_thermetry_layout
from layouts.dilutionfridge import create_dilutionFridge_layout
from layouts.cryocmp import create_cryocmp_layout
from callbacks.callbacks import register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Create the main layout with a vertical nav bar
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("TolTEC Dashboard", className="text-center mb-4"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Thermetry", href="#", id="thermetry-link", active=True)),
                dbc.NavItem(dbc.NavLink("Dilution Fridge", href="#", id="dilution-fridge-link")),
                dbc.NavItem(dbc.NavLink("Cryocmp", href="#", id="cryocmp-link")),
            ],
            vertical=True,
            pills=True,
            ),
        ], width=2, className="bg-light"),
        dbc.Col([
            html.Div(id="content")
        ], width=10)
    ])
], fluid=True)


@app.callback(
    [Output("content", "children"),
     Output("thermetry-link", "active"),
     Output("dilution-fridge-link", "active"),
     Output("cryocmp-link", "active")],
    [Input("thermetry-link", "n_clicks"),
     Input("dilution-fridge-link", "n_clicks"),
     Input("cryocmp-link", "n_clicks")]
)
def render_content(thermetry_clicks, dilution_fridge_clicks, cryocmp_clicks):
    # Determine which button was clicked

    if not ctx.triggered:
        return create_thermetry_layout(), True, False, False  # Default to thermetry

    button_id = ctx.triggered_id

    if button_id == "thermetry-link":
        return create_thermetry_layout(), True, False, False
    elif button_id == "dilution-fridge-link":
        return create_dilutionFridge_layout(), False, True, False
    elif button_id == "cryocmp-link":
        return create_cryocmp_layout(), False, False, True

    # Fallback, in case no button was clicked (shouldn't happen)
    return create_thermetry_layout(), True, False, False

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)