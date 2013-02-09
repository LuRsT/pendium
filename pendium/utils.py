from pendium import app


def load_config():
    # Load default config
    app.config.from_object('pendium.default_config')

    # Load config.py in server root
    try:
        app.config.from_object('config')
    except:
        pass

    # Load any other config passed via env
    try:
        app.config.from_envvar('PENDIUM_CONFIG')
    except:
        pass
