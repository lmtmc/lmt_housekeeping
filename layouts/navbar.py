import dash_bootstrap_components as dbc
from dash import html


def create_menu_bar(label, sub_nav_links, main_id, icon_id, dropdown_id):
    """
    Create a reusable menu bar component.

    :param label: str, the main label for the menu bar
    :param sub_nav_links: list of dicts, each containing 'label' and 'href' for sub-navigation links
    :param main_id: str, id for the main NavLink
    :param icon_id: str, id for the dropdown icon
    :param dropdown_id: str, id for the dropdown container
    :return: dbc.Nav component
    """
    return dbc.Nav([
        dbc.NavLink([
            dbc.Label(label),
            html.Span(html.I(className='bi bi-chevron-down', id=icon_id), className='ms-2'),
        ], id=main_id, href="#"),
        html.Div([
            dbc.NavLink(link['label'], href=link['href'], id=f"{link['label'].split('/')[-1]}-link",
                        className="sub-nav")
            for link in sub_nav_links
        ], id=dropdown_id, style={'display': 'none'}),
    ], vertical=True, pills=True, className='nav-custom')