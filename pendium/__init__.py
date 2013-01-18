from flask import Flask

app = Flask(__name__)

from pendium.utils import load_config

load_config()

import pendium.views 
