from callbacks.toltec.cryocmp_callback import cryocmp_register_callbacks
from callbacks.toltec.dilutionfridge_callback import dilutionfridge_register_callbacks
from callbacks.toltec.thermetry_callback import thermetry_register_callbacks
from callbacks.menu_bar_callback import menu_bar_callback
from callbacks.rsr.rsfend_callback import rsfend_register_callbacks

def register_callbacks(app):
    thermetry_register_callbacks(app)
    dilutionfridge_register_callbacks(app)
    cryocmp_register_callbacks(app)
    rsfend_register_callbacks(app)
    menu_bar_callback(app)
