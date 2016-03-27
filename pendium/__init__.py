from logging import getLogger
from logging import DEBUG

from flask import Flask


app = Flask(__name__)


loggers = [app.logger, getLogger('pendium.filesystem')]
for logger in loggers:
    logger.setLevel(DEBUG)

from pendium.load_config import load_config


import pendium.views


def run(config_file=None, wikipath=None):
    load_config(config_file)

    # This is quite dirty FIXME
    app.config['WIKI_DIR'] = wikipath

    app.run(host=app.config.get('WIKI_HOST_IP', '0.0.0.0'))
