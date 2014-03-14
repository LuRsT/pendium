from logging import getLogger
from logging import DEBUG

from flask import Flask


app = Flask(__name__)


loggers = [app.logger, getLogger('pendium.filesystem')]
for logger in loggers:
    logger.setLevel(DEBUG)

from pendium.load_config import load_config


load_config()


import pendium.views
