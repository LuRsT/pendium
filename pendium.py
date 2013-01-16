import os
import markdown

from config import Config
from flask  import Flask
from flask  import Markup
from flask  import render_template

class Pendium:
    def __init__(self, filename = None):
        self.cfg = Config( file( 'config' ) )

        if filename != None:
            self.filename = filename


    def get_md_files(self):
        filenames = []
        for filename in os.listdir( self.cfg.wiki_dir ):
            if filename[ filename.find('.') + 1: ] not in self.cfg.extensions:
                continue

            filenames.append( Pendium(filename) )

        return filenames


    def short_filename( self ):
        return self.filename.replace( '.', '_' )


    # This sucks
    def unshort_filename( self ):
        filename = self.filename[::-1]
        filename = filename.replace( '_', '.', 1 )
        return filename[::-1]


    def get_md_file( self ):
        complete_filename = '/'.join( [ self.cfg.wiki_dir,
                                        self.unshort_filename() ] )

        try:
            f = open( complete_filename, 'r' )
        except IOError as e:
            return "File not found."

        markdown_content = f.read().decode('utf-8')
        markdown_content = markdown.markdown( markdown_content, self.cfg.markdown_plugins )

        return Markup( markdown_content )


app = Flask(__name__)

@app.route('/')
def index():
    p = Pendium()
    return render_template( 'index.html', files = p.get_md_files(),
                                          config = p.cfg
                          )


@app.route('/<filename>')
def view( filename ):
    p = Pendium(filename)
    md_html = p.get_md_file()

    return render_template( 'view.html', filename = filename,
                                         files    = p.get_md_files(),
                                         markdown = md_html,
                                         config   = p.cfg
                          )

@app.route('/refresh/')
def refresh():
    p = Pendium()

    info = ''
    if p.cfg.git_support:
        try:
            import git
            repo = git.Repo( p.cfg.wiki_dir )
            info = repo.git.pull()
        except:
            info = 'Error refreshing'
            import sys
            print sys.exc_info()[0]

    return render_template( 'index.html', files = p.get_md_files(),
                                          info = info,
                                          config = p.cfg
                          )


if __name__ == '__main__':
    pendium = Pendium()

    if pendium.cfg.host_ip: # Run server externally
        app.debug = False
        app.run( host = pendium.cfg.host_ip )

    app.debug = True
    app.run()
