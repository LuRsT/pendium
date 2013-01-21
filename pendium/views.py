import os
import markdown

from flask import ( Flask, Markup, render_template, flash, redirect, url_for,
                    abort, g, request )

from pendium import app
from pendium.filesystem import ( Wiki, PathNotFound )

@app.route('/')
def index():
    p = g.wiki.root()
    return render_template( 'index.html', files = p.items() )

@app.route('/<path:path>')
def view( path ):
    try:
        p = g.wiki.get( path )
    except PathNotFound:
        abort(404)

    if p.is_leaf and p.can_render():
        return render_template( 'view.html', file     = p,
                                             files    = p.items(),
                                             rendered = p.render()
                              )
    elif p.is_node:
        return render_template( 'list.html', files = p.items(), file = p )
    else:
        #TODO: Download the file!
        pass

@app.route( '/search/', methods=[ 'GET', 'POST' ] )
def search():
    context = { 'searched' : False }

    if request.form.get('q', None):
        term = request.form.get('q')
        app.logger.debug("Searching for '%s'" % term )
        hits = g.wiki.search(term)
        context['searched'] = True
        context['term']     = term
        context['hits']     = len(hits)
        context['results']  = hits

    return render_template('search.html', **context)

@app.route('/refresh/')
def refresh():
    try:
        info = g.wiki.refresh()
        flash("Your wiki has been refreshed. %" % info, 'success')
    except Exception, e:
        app.logger.error( e )
        flash( "Error refreshing git repository", 'error' )

    return redirect( url_for('index') )

@app.context_processor
def global_context_data():
    data = { 'config': app.config }
    return data

@app.errorhandler(404)
def not_found( error ):
    return render_template('not_found.html'), 404

@app.before_request
def before_request():
    config = app.config
    g.wiki = Wiki( config['WIKI_DIR'],
                   extensions       = config.get( 'WIKI_EXTENSIONS',       {}    ),
                   default_renderer = config.get( 'WIKI_DEFAULT_RENDERER', None  ),
                   plugins_config   = config.get( 'WIKI_PLUGINS_CONFIG',   {}    ),
                   git_support      = config.get( 'WIKI_GIT_SUPPORT',      False )
                 )
