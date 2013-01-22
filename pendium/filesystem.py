import os
import codecs

from yapsy.PluginManager import PluginManager
from flask               import current_app
from pendium.plugins     import IRenderPlugin, ISearchPlugin

import logging
logger = logging.getLogger(__name__)

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

class NoSearchPluginAvailable( Exception ):
    pass

class Wiki( object ):
    def __init__( self, basepath, extensions={}, default_renderer=None,
                        plugins_config={}, git_support=False ):
        self.basepath         = basepath
        self.extensions       = extensions
        self.default_renderer = default_renderer
        self.git_support      = git_support

        for name, configuration in plugins_config.items():

            for cat in ["Search", "Render"]:
                plugin = manager.getPluginByName( "%s" % name, category=cat )
                if not plugin:
                    continue

                logger.debug( "Configuring plugin: %s with :%s" % (name, configuration) ) 
                plugin.plugin_object.configure( configuration )


    def search( self, term ):
        best_plugin_score = 0
        best_plugin       = None
        for plugin in manager.getPluginsOfCategory('Search'):
            if plugin.plugin_object.search_speed > best_plugin_score:
                best_plugin_score = plugin.plugin_object.search_speed
                best_plugin       = plugin

        if best_plugin is None:
            raise NoSearchPluginAvailable

        logger.debug( "Searching with %s" % best_plugin.name ) 

        return best_plugin.plugin_object.search( self, term )


    def root( self ):
        return self.get( '.' )


    def get( self, path ):
        completepath = os.path.join( self.basepath, path )
        if os.path.isdir( completepath ):
            return WikiDir( self, path )
        else:
            return WikiFile( self, path )


    def create( self, path ):
        new_abs_path = os.path.join( self.basepath, path )
        fp = file( new_abs_path, 'w' )
        fp.close()
        return WikiFile( self, path )


    def refresh(self):
        if not self.git_support:
            return ''

        if self.git_repo_branch_has_remote():
            return self.git_repo().git.pull()

        return ''


    def git_repo_branch_has_remote(self):
        repo = self.git_repo()
        #check if this is a remote name
        try:
            branch = repo.active_branch
            remote = branch.remote_name
            if remote:
                return True
            else:
                return False
        except:
            return False


    def git_repo(self):
        try:
            import git
            repo = git.Repo( self.basepath )
            return repo
        except ImportError, e:
            raise Exception( "Could not import git module" )


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

    @property
    def editable(self):
        return os.access(self.abs_path , os.W_OK)

class WikiFile( WikiPath ):
    def __init__( self, *args, **kwargs ):
        super( WikiFile, self ).__init__( *args, **kwargs )
        self.is_leaf   = True
        self.extension = os.path.splitext( self.name )[1][1:]


    def renderer( self ):
        for plugin in manager.getPluginsOfCategory('Render'):
            logger.debug( "Testing for plugin %s", plugin.plugin_object.name )
            extensions = self.wiki.extensions.get(plugin.plugin_object.name, None)
            if extensions is None:
                continue #try the next plugin

            if self.extension in extensions:
                logger.debug(self.extension)
                logger.debug(plugin.plugin_object.name)
                return plugin.plugin_object

        #if no renderer found and binary, give up
        if self.is_binary:
            return None

        #if is not binary and we have a default renderer
        # return it
        if self.wiki.default_renderer:
            return self.wiki.default_renderer

        return None


    @property
    def can_render( self ):
        return bool( self.renderer )


    def render( self ):
        if self.can_render:
            renderer = self.renderer()
            return renderer.render( self.content() )

        # No renderer found!
        raise CannotRender( self.abs_path )


    @property
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


    def content(self, content=None):
        fp = open(self.abs_path, 'r')
        ct = fp.read().decode( 'utf-8' )
        fp.close()

        if not content:
            return ct

        if content == ct:
            return ct

        # Save the file
        fp = open(self.abs_path, 'w')
        fp.write( content )
        fp.close()

        if self.wiki.git_support:
            repo = self.wiki.git_repo()
            repo.git.add( self.path )
            repo.git.commit( m='New content version' )

            if self.wiki.git_repo_branch_has_remote():
                repo.git.push()

        return content

class WikiDir( WikiPath ):
    def __init__( self, *args, **kwargs ):
        super( WikiDir, self ).__init__( *args, **kwargs )
        self.is_node = True
