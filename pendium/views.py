import os
import markdown

from flask  import (Flask, Markup, render_template, flash, redirect, url_for,
                    abort, g)

from pendium import app, config 

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

    if p.is_leaf:
        md_html = p.get_md_file()

        return render_template( 'view.html',  file     = p,
                                              files    = p.items(),
                                              markdown = md_html
                              )
    elif p.is_node:
        return render_template( 'list.html', files = p.items(), file = p )

@app.route('/refresh/')
def refresh():
    if config.git_support:
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
