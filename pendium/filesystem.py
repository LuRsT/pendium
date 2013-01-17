import os
import markdown

from flask import Markup

class PathNotFound(Exception):
    pass

class Wiki(object):
    def __init__(self, basepath, config=None):
        self.basepath = basepath
        self.config   = config

    def root(self):
        return self.get( '.' )

    def get(self, path):
        completepath = os.path.join( self.basepath, path )
        if os.path.isdir( completepath ):
            return WikiDir( self, path )
        else:
            return WikiFile( self, path )

class WikiPath(object):
    def __init__( self, wiki, path ):
        self.path     = path
        self.wiki     = wiki
        self.abs_path = os.path.join( wiki.basepath , path )
        self.abs_path = os.path.normpath( self.abs_path )
        self.name     = os.path.split( self.path )[1]
        self.is_node  = False
        self.is_leaf  = False

        if not os.path.exists( self.abs_path ):
            raise PathNotFound( self.abs_path )

        if os.path.isdir( self.abs_path ):
            self.is_node = True
        else:
            self.is_leaf = True

    def ancestor( self ):
        if self.path == '':
            return None
        return self.wiki.get( os.path.split( self.path )[0] )

    def ancestors( self ):
        if self.ancestor():
            return self.ancestor().ancestors() + [ self.ancestor() ]
        return []

    def items( self ):
        if not os.path.isdir( self.abs_path ):
            self = self.ancestor()

        filenames = []
        for f in os.listdir( self.abs_path ):
            complete_abs_path = os.path.join( self.abs_path, f )
            complete_path     = os.path.join( self.path, f )

            if ( f.find('.') == 0 ):
                continue

            if os.path.isdir( complete_abs_path ):
                filenames.append( self.wiki.get( complete_path ) )
            elif f[ f.find('.') + 1: ] in self.wiki.config.extensions:
                filenames.append( self.wiki.get( complete_path ) )

        return filenames

class WikiFile( WikiPath ):
    def __init__(self, *args, **kwargs ):
        super( WikiFile, self ).__init__( *args, **kwargs )
        self.is_leaf = True

    def get_md_file( self ):
        complete_filename = self.abs_path

        try:
            f = open( complete_filename, 'r' )
        except IOError as e:
            return "File not found."

        markdown_content = f.read().decode('utf-8')
        markdown_content = markdown.markdown( markdown_content, self.wiki.config.markdown_plugins )

        return Markup( markdown_content )

class WikiDir( WikiPath ):
    def __init__(self, *args, **kwargs ):
        super( WikiDir, self ).__init__( *args, **kwargs )
        self.is_node = True
