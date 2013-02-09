from pendium import app


def load_config():
    #Load default config
    app.config.from_object('pendium.default_config')

    #load config.py in server root
    try:
        app.config.from_object('config')
    except:
        pass

    #load any other config passed via env
    try:
        app.config.from_envvar('PENDIUM_CONFIG')
    except:
        pass
