import os

from yapsy.PluginManager import PluginManager
from flask import current_app
from pendium.plugins import IRenderPlugin, ISearchPlugin

# Populate plugins
manager = PluginManager()
manager.setPluginPlaces( ["pendium/plugins"] )
manager.setCategoriesFilter({
                        "Search" : ISearchPlugin,
                        "Render" : IRenderPlugin,
                        })
manager.collectPlugins()

class PathNotFound( Exception ):
    pass

class CannotRender( Exception ):
    pass

class Wiki( object ):
    def __init__( self, basepath, extensions={}, default_renderer=None,
                       markdown_plugins=[], git_support=False ):
        self.basepath         = basepath
        self.extensions       = extensions
        self.default_renderer = default_renderer
        self.markdown_plugins = markdown_plugins
        self.git_support      = git_support

    def root( self ):
        return self.get( '.' )

    def get( self, path ):
        completepath = os.path.join( self.basepath, path )
        if os.path.isdir( completepath ):
            return WikiDir( self, path )
        else:
            return WikiFile( self, path )

    def refresh(self):
        if not self.git_support:
            return ''

        try:
            import git
            repo = git.Repo( self.basepath )
            return repo.git.pull()
        except ImportError, e:
            raise Exception( "Could not import git module" )
        except:
            import sys
            raise Exception( sys.exc_info()[0] )

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
            if ( f.find('.') == 0 ):
                continue

            complete_path = os.path.join( self.path, f )
            filenames.append( self.wiki.get( complete_path ) )

        return filenames

class WikiFile( WikiPath ):
    def __init__( self, *args, **kwargs ):
        super( WikiFile, self ).__init__( *args, **kwargs )
        self.is_leaf   = True
        self.extension = os.path.splitext(self.name)[1][1:]


    def renderer( self ):
        for plugin in manager.getPluginsOfCategory('Render'):
            current_app.logger.debug("Testing for plugin %s", plugin.plugin_object.name)
            extensions = self.wiki.extensions.get(plugin.plugin_object.name, None)
            if extensions is None:
                continue #try the next plugin

            if self.extension in extensions:
                current_app.logger.debug(self.extension)
                current_app.logger.debug(plugin.plugin_object.name)
                return plugin.plugin_object 


        #if no renderer found and binary, give up
        if self.is_binary():
            return None

        #if is not binary and we have a default renderer
        # return it
        if self.wiki.default_renderer:
            return self.wiki.default_renderer

        return None

    def can_render( self ):
        return bool( self.renderer )

    def render( self ):
        if self.can_render:
            renderer = self.renderer()
            content = open( self.abs_path, 'r' ).read().decode( 'utf-8' )
            return renderer.render( content )

        # No renderer found!
        raise CannotRender( self.abs_path )

    def is_binary(self):
        """Return true if the file is binary."""
        fin = open(self.abs_path, 'rb')
        try:
            CHUNKSIZE = 1024
            while 1:
                chunk = fin.read( CHUNKSIZE )
                if '\0' in chunk: # found null byte
                    return  True
                if len( chunk ) < CHUNKSIZE:
                    break # done
        finally:
            fin.close()

        return False

class WikiDir( WikiPath ):
    def __init__( self, *args, **kwargs ):
        super( WikiDir, self ).__init__( *args, **kwargs )
        self.is_node = True
