import os
import markdown

from config import Config
from flask  import (Flask, Markup, render_template, flash, redirect, url_for,
                    abort, g)
from pendium.filesystem import Wiki 

config = None

app = Flask(__name__)
app.secret_key = 'pendiumissopendular'

config = Config( file( 'config' ) )
app.logger.debug( "Loading config" )

if config.host_ip: # Run server externally
    app.debug = False
    app.run( host = config.host_ip )

app.debug = True

import pendium.views 

@app.context_processor
def global_context_data():
    data = { 'config': config }
    return data

@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404

@app.before_request
def before_request():
    g.wiki = Wiki( config.wiki_dir, config=config ) 
