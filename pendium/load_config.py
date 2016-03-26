from pendium import app


def load_config(config_file=None):
    app.config.from_object('pendium.default_config')

    if config_file:
        app.config.from_pyfile(config_file, silent=False)

    # Load any other config passed via env
    try:
        app.config.from_envvar('PENDIUM_CONFIG')
    except:
        pass
