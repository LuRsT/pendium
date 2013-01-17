import os
import markdown

from config import Config
from flask  import (Flask, Markup, render_template, flash, redirect, url_for,
                    abort)

config = None

class PendiumPathNotFound(Exception):
    pass

class Pendium:
    def __init__( self, path ):
        self.path     = path
        self.abs_path = os.path.join( config.wiki_dir, path )
        self.abs_path = os.path.normpath( self.abs_path )
        self.name     = os.path.split( self.path )[1]
        self.is_node  = False
        self.is_leaf  = False

        if not os.path.exists( self.abs_path ):
            raise PendiumPathNotFound( self.abs_path )

        if os.path.isdir( self.abs_path ):
            self.is_node = True
        else:
            self.is_leaf = True

    def ancestor( self ):
        if self.path == '':
            return None
        return Pendium( os.path.split( self.path )[0] )

    def ancestors( self ):
        if self.ancestor():
            return self.ancestor().ancestors() + [ self.ancestor() ]
        return []

    # Returns the files of the path object, if it's a file,
    # return it's ancestor's files
    def items( self ):
        obj = self
        if not os.path.isdir( self.abs_path ):
            obj = self.ancestor()

        filenames = []
        for f in os.listdir( obj.abs_path ):
            complete_abs_path = os.path.join( obj.abs_path, f )
            complete_path     = os.path.join( obj.path, f )

            if ( f.find('.') == 0 ):
                continue

            if os.path.isdir( complete_abs_path ):
                filenames.append( Pendium( complete_path ) )
            elif f[ f.find('.') + 1: ] in config.extensions:
                filenames.append( Pendium( complete_path ) )

        return filenames

    def get_md_file( self ):
        complete_filename = self.abs_path

        try:
            f = open( complete_filename, 'r' )
        except IOError as e:
            return "File not found."

        markdown_content = f.read().decode('utf-8')
        markdown_content = markdown.markdown( markdown_content, config.markdown_plugins )

        return Markup( markdown_content )

app = Flask(__name__)
app.secret_key = 'pendiumissopendular'

@app.context_processor
def global_context_data():
    data = { 'config': config }
    return data

@app.route('/')
def index():
    p = Pendium( '.' )
    return render_template( 'index.html', files = p.items() )

@app.route('/<path:path>')
def view( path ):
    try:
        p = Pendium( path )
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

@app.errorhandler(404)
def not_found(error):
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    config = Config( file( 'config' ) )

    if config.host_ip: # Run server externally
        app.debug = False
        app.run( host = config.host_ip )

    app.debug = True
    app.run()
