from logging import getLogger
from os import W_OK as CAN_WRITE
from os import access as can_access
from os import listdir as list_dir
from os import makedirs as make_dirs
from os import remove as remove_file
from os import rmdir as remove_dir
from os import walk
from os.path import abspath
from os.path import dirname
from os.path import exists as path_exists
from os.path import isdir as is_dir
from os.path import join as join_path
from os.path import normpath
from os.path import split as split_path
from os.path import splitext as split_text
import codecs

from pendium import app
from pendium.plugins import IRenderPlugin
from pendium.search import get_hits_for_term_in_wiki
from yapsy.PluginManager import PluginManager


_LOGGER = getLogger(__name__)


# Populate plugins
lib_path = abspath(dirname(__file__))
manager = PluginManager()
manager.setPluginPlaces([join_path(lib_path, 'plugins')])
manager.setCategoriesFilter({'Render': IRenderPlugin})
manager.collectPlugins()


class PathExists(Exception):
    pass


class PathNotFound(Exception):
    pass


class Wiki(object):
    def __init__(
        self,
        basepath,
        extensions={},
        default_renderer=None,
        plugins_config={},
        has_vcs=False,
    ):
        self.basepath = basepath
        self.extensions = extensions
        self.default_renderer = default_renderer
        self.has_vcs = has_vcs
        self.vcs = None

        if self.has_vcs:
            try:
                from pendium import git_wrapper
                self.vcs = git_wrapper.GitWrapper(basepath)
            except:
                raise Exception('You need to install GitPython')

        # Plugin configuration
        for name, configuration in plugins_config.items():
            for cat in ['Render']:
                plugin = manager.getPluginByName(name, category=cat)
                if not plugin:
                    continue

                msg = 'Configuring plugin: %s with :%s' % (name, configuration)
                _LOGGER.debug(msg)
                plugin.plugin_object.configure(configuration)

    def search(self, term):
        return get_hits_for_term_in_wiki(self, term)

    def get_root(self):
        return self.get('.')

    def get(self, path):
        complete_path = join_path(self.basepath, path)
        complete_path = normpath(complete_path)
        if is_dir(complete_path):
            return WikiDir(self, path)
        else:
            return WikiFile(self, path)

    def refresh(self):
        if self.has_vcs:
            return self.vcs.refresh()


class WikiPath(object):

    def __init__(self, wiki, path):
        self.path = path
        self.wiki = wiki
        self.abs_path = join_path(wiki.basepath, path)
        self.abs_path = normpath(self.abs_path)
        self.name = split_path(self.path)[1]
        self.is_node = False
        self.is_leaf = False

        if not path_exists(self.abs_path):
            raise PathNotFound(self.abs_path)

    def ancestor(self):
        if not self.path:
            return None

        ancestor_dir = split_path(self.path)[0]
        return self.wiki.get(ancestor_dir)

    def ancestors(self):
        if self.ancestor():
            return self.ancestor().ancestors() + [self.ancestor()]
        return []

    def items(self):
        if not is_dir(self.abs_path):
            self = self.ancestor()

        filenames = []
        for file_path in list_dir(unicode(self.abs_path)):
            if (file_path.find('.') == 0):
                continue

            if (split_text(file_path)[1][1:]
                    in app.config['BLACKLIST_EXTENSIONS']):
                continue

            complete_path = join_path(self.path, file_path)
            filenames.append(self.wiki.get(complete_path))

        return sorted(filenames, key=lambda Wiki: Wiki.is_leaf)

    @property
    def editable(self):
        if app.config['EDITABLE']:
            return can_access(self.abs_path, CAN_WRITE)
        return False

    def delete(self):
        top = self.abs_path
        for root, dirs, files in walk(top, topdown=False):
            for name in files:
                _LOGGER.debug('Will remove FILE: %s', join_path(root, name))
                remove_file(join_path(root, name))
            for name in dirs:
                _LOGGER.debug('Will remove DIR: %s', join_path(root, name))
                remove_dir(join_path(root, name))

        if self.is_node:
            _LOGGER.debug('Will remove DIR: %s', self.abs_path)
            remove_dir(self.abs_path)
        else:
            _LOGGER.debug('Will remove FILE: %s', self.abs_path)
            remove_file(self.abs_path)

        if self.wiki.has_vcs:
            self.wiki.vcs.delete(path=self.path)


class WikiFile(WikiPath):

    def __init__(self, *args, **kwargs):
        super(WikiFile, self).__init__(*args, **kwargs)
        self.is_leaf = True
        self.extension = split_text(self.name)[1][1:]
        self._content = ''

    def renderer(self):
        for plugin in manager.getPluginsOfCategory('Render'):
            _LOGGER.debug('Testing for plugin %s', plugin.plugin_object.name)
            extensions = self.wiki.extensions.get(plugin.plugin_object.name,
                                                  None)
            if extensions is None:
                continue  # Try the next plugin

            if self.extension in extensions:
                _LOGGER.debug(self.extension)
                _LOGGER.debug(plugin.plugin_object.name)
                return plugin.plugin_object

        # If no renderer found and binary, give up
        if self.is_binary:
            return None

        # If is not binary and we have a default renderer
        # return it
        if self.wiki.default_renderer:
            return self.wiki.default_renderer

        return None

    @property
    def can_render(self):
        return bool(self.renderer())

    def render(self):
        if self.can_render:
            renderer = self.renderer()
            return renderer.render(self.content())

        # No renderer found
        if self.is_binary:
            return self.content(decode=False)

        return self.content()

    @property
    def is_binary(self):
        """
        Return true if the file is binary.

        """
        fin = open(self.abs_path, 'rb')
        try:
            CHUNKSIZE = 1024
            while 1:
                chunk = fin.read(CHUNKSIZE)
                if '\0' in chunk:  # Found null byte
                    return True
                if len(chunk) < CHUNKSIZE:
                    break  # Done
        finally:
            fin.close()

        return False

    @property
    def refs(self):
        """
        Special property for Git refs

        """
        if self.wiki.has_vcs:
            return self.wiki.vcs.file_refs(self.path)

        return []

    def ref(self, ref):
        """
        Update file content with appropriate reference from git to display
        older file versions

        """
        try:
            content = self.wiki.vcs.show(filepath=self.path, ref=ref)
            self._content = content.decode('utf8')
            return True
        except:
            return False

    def content(self, content=None, decode=True):
        """
        Helper method, needs refactoring

        """
        if self._content and content is None:
            return self._content

        with open(self.abs_path, 'r') as file_obj:
            file_content = file_obj.read()

        if decode:
            file_content = file_content.decode('utf-8')

        if not content:
            self._content = file_content
            return file_content

        self._content = content

        if content == file_content:
            return file_content

    def save(self, comment=None):
        file_obj = codecs.open(self.abs_path, 'w', 'utf-8')
        file_obj.write(self._content)
        file_obj.close()

        if self.wiki.has_vcs:
            self.wiki.vcs.save(path=self.path, comment=comment)


class WikiDir(WikiPath):

    def __init__(self, *args, **kwargs):
        super(WikiDir, self).__init__(*args, **kwargs)
        self.is_node = True

    def create_file(self, filename):
        new_abs_path = join_path(self.abs_path, filename)
        if path_exists(new_abs_path):
            raise PathExists(new_abs_path)
        file_obj = file(new_abs_path, 'w')
        file_obj.close()
        return self.wiki.get(join_path(self.path, filename))

    def create_directory(self, name):
        new_abs_path = join_path(self.abs_path, name)
        if path_exists(new_abs_path):
            raise PathExists(new_abs_path)

        make_dirs(new_abs_path)
        np = self.wiki.get(join_path(self.path, name))
        return np
