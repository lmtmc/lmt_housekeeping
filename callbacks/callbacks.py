from callbacks.cryocmp_callback import cryocmp_register_callbacks
from callbacks.dilutionfridge_callback import dilutionfridge_register_callbacks
from callbacks.thermetry_callback import thermetry_register_callbacks

def register_callbacks(app):
    thermetry_register_callbacks(app)
    dilutionfridge_register_callbacks(app)
    cryocmp_register_callbacks(app)
