import os
import markdown
import traceback

from flask import ( Flask, Markup, render_template, flash, redirect, url_for,
                    abort, g, request, escape )

from pendium import app
from pendium.filesystem import ( Wiki, PathNotFound, PathExists )

@app.route('/')
def index():
    p = g.wiki.root()
    return render_template( 'index.html', files = p.items() )


@app.route('/_create_/',            methods=[ 'GET', 'POST' ] )
@app.route('/_create_/<path:path>', methods=[ 'GET', 'POST' ] )
def create( path=None ):
    p = g.wiki.root()
    if path != None:
        try:
            p = g.wiki.get( path )
        except PathNotFound:
            abort(404)

    if not p.is_node:
        abort(500)

    filename   =None
    filecontent=None

    if request.form.get('save', None):
        filename    = request.form.get('filename')
        filecontent = request.form.get('content')
        try:
            new_file = p.create( filename )
            new_file.content( filecontent )
            flash("File created with the provided content", 'success')
            return redirect( url_for('view', path=path) )
        except PathExists, pe:
            app.logger.error( traceback.format_exc() )
            flash("There is already a file by that name", 'error')
            
        except Exception, e:
            app.logger.error( traceback.format_exc() )
            flash("There was a problem saving your file : %s" % e, 'error')

    return render_template( 'create.html', file = p, filename=filename, filecontent=filecontent )


@app.route('/_edit_/<path:path>', methods=[ 'GET', 'POST' ] )
def edit( path ):
    try:
        p = g.wiki.get( path )
    except PathNotFound:
        abort(404)

    if not p.is_leaf:
        abort(500)

    if p.is_binary:
        abort(500)

    content = p.content()
    if request.form.get('save', None):
        content = request.form.get('content')
        try:
            p.content( content )
            flash("File saved with the new provided content", 'success')
            return redirect( url_for('view', path=path) )
        except Exception, e:
            app.logger.error( traceback.format_exc() )
            flash("There was a problem saving your file : %s" % e, 'error')

    return render_template( 'edit.html', file         = p,
                                         files        = p.items(),
                                         file_content = escape(content),
                          )


@app.route('/<path:path>')
def view( path ):
    try:
        p = g.wiki.get( path )
    except PathNotFound:
        abort(404)

    if p.is_leaf and p.can_render:
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
        flash("Your wiki has been refreshed. %s" % info, 'success')
    except Exception, e:
        app.logger.error( e )
        app.logger.error( traceback.format_exc() )
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
