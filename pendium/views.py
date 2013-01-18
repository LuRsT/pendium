import os
import markdown

from flask  import (Flask, Markup, render_template, flash, redirect, url_for,
                    abort, g)

from pendium.filesystem import Wiki
from pendium import app

@app.route('/')
def index():
    p = g.wiki.root() 
    return render_template( 'index.html', files = p.items() )

@app.route('/<path:path>')
def view( path ):
    try:
        p = g.wiki.get( path )
    except PendiumPathNotFound:
        abort(404) 

    if p.is_leaf and p.can_render():
        return render_template( 'view.html',  file     = p,
                                              files    = p.items(),
                                              rendered = p.render()
                              )
    elif p.is_node:
        return render_template( 'list.html', files = p.items(), file = p )
    else:
        #TODO: Download the file!
        pass

@app.route('/refresh/')
def refresh():
    if app.config.get('WIKI_GIT_SUPPORT', False):
        try:
            import git
            repo = git.Repo( '.' )
            info = repo.git.pull()
            flash(info, 'success')
        except:
            import sys
            app.logger.error( sys.exc_info()[0] )
            flash( "Error refreshing git repository", 'error' )

    return redirect(url_for('index'))

@app.context_processor
def global_context_data():
    data = { 'config': app.config }
    return data

@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404

@app.before_request
def before_request():
    config = app.config
    g.wiki = Wiki( config['WIKI_DIR'], 
                   extensions=config.get('WIKI_EXTENSIONS',{}),
                   default_renderer=config.get('WIKI_DEFAULT_RENDERER',None),
                   markdown_plugins=config.get('WIKI_MARKDOWN_PLUGINS',[]),
                   git_support=config.get('WIKI_GIT_SUPPORT',False)
                 )
