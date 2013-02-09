from flask import Flask
import logging

app = Flask(__name__)

loggers = [app.logger, logging.getLogger('pendium.filesystem')]
for logger in loggers:
    logger.setLevel(logging.DEBUG)

from pendium.utils import load_config

load_config()

import pendium.views
