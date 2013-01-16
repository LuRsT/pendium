import os
import markdown

from config import Config
from flask  import Flask, Markup, render_template

config = None

class Pendium:
    def __init__(self, path):
        self.path     = path
        self.abs_path = os.path.join(config.wiki_dir, path)
        self.name     = os.path.split(self.abs_path)[1] 
        self.is_node  = False
        self.is_leaf  = False

        if os.path.isdir( self.abs_path ):
            self.is_node = True
        else:
            self.is_leaf = True

    def items(self):
        filenames = []
        if not os.path.isdir(self.abs_path):
            return filenames
             
        for f in os.listdir( self.abs_path ):
            complete_abs_path = os.path.join( self.abs_path, f )
            complete_path     = os.path.join( self.path, f )
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

@app.route('/')
def index():
    p = Pendium( '.' )
    return render_template( 'index.html', files=p.items() )


@app.route('/<path:path>')
def view( path ):
    p = Pendium( path )

    if p.is_leaf:
        md_html = p.get_md_file()

        return render_template( 'view.html',  file     = p,
                                              files    = p.items(),
                                              markdown = md_html
                              )
    elif p.is_node:
        return render_template( 'list.html', files=p.items(), file=p )

if __name__ == '__main__':
    config = Config( file( 'pendium.cfg' ) )

    if config.host_ip: # Run server externally
        app.debug = False
        app.run( host = config.host_ip )

    app.debug = True
    app.run()
