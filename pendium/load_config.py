from pendium import app


def load_config():
    # Load default config
    app.config.from_object('pendium.default_config')

    # Load config.py in server root
    app.config.from_pyfile('config.py', silent=True)

    # Load any other config passed via env
    try:
        app.config.from_envvar('PENDIUM_CONFIG')
    except:
        pass
