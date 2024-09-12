import dash_bootstrap_components as dbc
from dash import html
import yaml

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
prefix = config['prefix']

def create_sub_menu_bar(label, sub_nav_links, main_id, icon_id, dropdown_id, ):
    return dbc.Nav([
        dbc.NavLink([
            dbc.Label(label, className='me-auto'),
            html.Span(html.I(className='bi bi-chevron-down', id=icon_id),),
        ], id=main_id, href="#", className='d-flex align-items-center'),
        html.Div([
            dbc.NavLink(
                link['label'],
                href=link['href'],
                id=f"{link['href'].split('/')[-1]}-link",
                active='exact',
                className="sub-nav"
            )
            for link in sub_nav_links
        ], id=dropdown_id, style={'display': 'none'}),
    ], vertical=True, pills=True, className='nav-custom')

toltec_menu = create_sub_menu_bar('TolTEC',
                              sub_nav_links=[
                                    {'label': 'Thermetry', 'href': f'{prefix}/thermetry'},
                                    {'label': 'Dilution Fridge', 'href': f'{prefix}/dilutionFridge'},
                                    {'label': 'Cryocmp', 'href': f'{prefix}/cryocmp'},
                              ],
                              main_id='toltec-dashboard-link',
                              icon_id='toltec-icon',
                              dropdown_id='toltec-dropdown')
rsr_menu = create_sub_menu_bar('RSR',
                          sub_nav_links=[
                              {'label': 'RSR', 'href': f'{prefix}/rsfend'},
                          ],
                          main_id='rsr-dashboard-link',
                          icon_id='rsr-icon',
                          dropdown_id='rsr-dropdown')

def create_menu_bar():
    return [toltec_menu, rsr_menu]