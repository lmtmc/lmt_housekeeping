from dash import Output, Input, State
import yaml
with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
prefix = config['prefix']


def menu_bar_callback(app):
    @app.callback(
        Output('toltec-dropdown', 'style'),
        Output('toltec-icon', 'className'),
        Input('toltec-dashboard-link', 'n_clicks'),
        State('toltec-dropdown', 'style'),
        prevent_initial_call=True
    )
    def toltec_toggle_dropdown(n_clicks, dropdown_style):
        if n_clicks:
            is_open = dropdown_style['display'] == 'block'
            return (
                {'display': 'none' if is_open else 'block'},
                'bi bi-chevron-down' if is_open else 'bi bi-chevron-up'
            )
        return dropdown_style, 'bi bi-chevron-down'

    @app.callback(
        Output('rsr-dropdown', 'style'),
        Output('rsr-icon', 'className'),
        Input('rsr-dashboard-link', 'n_clicks'),
        State('rsr-dropdown', 'style'),
        prevent_initial_call=True
    )
    def rsr_toggle_dropdown(n_clicks, dropdown_style):
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