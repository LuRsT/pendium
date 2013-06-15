import os
import codecs

from yapsy.PluginManager import PluginManager
from pendium.plugins import IRenderPlugin, ISearchPlugin
from pendium import app, git_wrapper

import logging
log = logging.getLogger(__name__)

# Populate plugins
lib_path = os.path.abspath(os.path.dirname(__file__))
manager = PluginManager()
manager.setPluginPlaces([os.path.join(lib_path, 'plugins')])
manager.setCategoriesFilter({"Search": ISearchPlugin,
                             "Render": IRenderPlugin})
manager.collectPlugins()


class PathExists(Exception):
    pass


class PathNotFound(Exception):
    pass


class CannotRender(Exception):
    pass


class NoSearchPluginAvailable(Exception):
    pass


class Wiki(object):
    def __init__(self,
                 basepath,
                 extensions={},
                 default_renderer=None,
                 plugins_config={},
                 has_vcs=False):
        self.basepath = basepath
        self.extensions = extensions
        self.default_renderer = default_renderer
        self.has_vcs = has_vcs
        self.vcs = None

        if self.has_vcs:
            # Use git since it's the only supported vcs
            self.vcs = git_wrapper.GitWrapper(basepath)

        # Plugin configuration
        for name, configuration in plugins_config.items():
            for cat in ["Search", "Render"]:
                plugin = manager.getPluginByName(name, category=cat)
                if not plugin:
                    continue

                msg = "Configuring plugin: %s with :%s" % (name, configuration)
                log.debug(msg)
                plugin.plugin_object.configure(configuration)

    def search(self, term):
        best_plugin_score = 0
        best_plugin = None
        for plugin in manager.getPluginsOfCategory('Search'):
            if plugin.plugin_object.search_speed > best_plugin_score:
                best_plugin_score = plugin.plugin_object.search_speed
                best_plugin = plugin

        if best_plugin is None:
            raise NoSearchPluginAvailable

        log.debug("Searching with %s" % best_plugin.name)

        return best_plugin.plugin_object.search(self, term)

    def root(self):
        return self.get('.')

    def get(self, path):
        completepath = os.path.normpath(os.path.join(self.basepath, path))
        if os.path.isdir(completepath):
            return WikiDir(self, path)
        else:
            return WikiFile(self, path)

    def refresh(self):
        if not self.has_vcs:
            return ''

        return self.vcs.refresh()


class WikiPath(object):
    def __init__(self, wiki, path):
        self.path = path
        self.wiki = wiki
        self.abs_path = os.path.join(wiki.basepath, path)
        self.abs_path = os.path.normpath(self.abs_path)
        self.name = os.path.split(self.path)[1]
        self.is_node = False
        self.is_leaf = False

        if not os.path.exists(self.abs_path):
            raise PathNotFound(self.abs_path)

    def ancestor(self):
        if self.path == '':
            return None
        ancestor_dir = os.path.split(self.path)[0]
        return self.wiki.get(ancestor_dir)

    def ancestors(self):
        if self.ancestor():
            return self.ancestor().ancestors() + [self.ancestor()]
        return []

    def items(self):
        if not os.path.isdir(self.abs_path):
            self = self.ancestor()

        filenames = []
        for f in os.listdir(unicode(self.abs_path)):
            if (f.find('.') == 0):
                continue

            if (os.path.splitext(f)[1][1:]
                    in app.config['BLACKLIST_EXTENSIONS']):
                continue

            complete_path = os.path.join(self.path, f)
            filenames.append(self.wiki.get(complete_path))

        return sorted(filenames, key=lambda Wiki: Wiki.is_leaf)

    @property
    def editable(self):
        if app.config['EDITABLE']:
            return os.access(self.abs_path, os.W_OK)
        return False

    def delete(self):
        top = self.abs_path
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                log.debug("Will remove FILE: %s", os.path.join(root, name))
                os.remove(os.path.join(root, name))
            for name in dirs:
                log.debug("Will remove DIR: %s", os.path.join(root, name))
                os.rmdir(os.path.join(root, name))

        if self.is_node:
            log.debug("Will remove DIR: %s", self.abs_path)
            os.rmdir(self.abs_path)
        else:
            log.debug("Will remove FILE: %s", self.abs_path)
            os.remove(self.abs_path)

        if self.wiki.has_vcs:
            self.wiki.vcs.delete(path=self.path)


class WikiFile(WikiPath):
    def __init__(self, *args, **kwargs):
        super(WikiFile, self).__init__(*args, **kwargs)
        self.is_leaf = True
        self.extension = os.path.splitext(self.name)[1][1:]
        self._content = ''

    def renderer(self):
        for plugin in manager.getPluginsOfCategory('Render'):
            log.debug("Testing for plugin %s", plugin.plugin_object.name)
            extensions = self.wiki.extensions.get(plugin.plugin_object.name,
                                                  None)
            if extensions is None:
                continue  # Try the next plugin

            if self.extension in extensions:
                log.debug(self.extension)
                log.debug(plugin.plugin_object.name)
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

        fp = open(self.abs_path, 'r')
        ct = fp.read()
        if decode:
            ct = ct.decode('utf-8')
        fp.close()

        if not content:
            self._content = ct
            return ct

        self._content = content

        if content == ct:
            return ct

    def save(self, comment=None):
        fp = codecs.open(self.abs_path, 'w', 'utf-8')
        fp.write(self._content)
        fp.close()

        if self.wiki.has_vcs:
            self.wiki.vcs.save(path=self.path, comment=comment)


class WikiDir(WikiPath):
    def __init__(self, *args, **kwargs):
        super(WikiDir, self).__init__(*args, **kwargs)
        self.is_node = True

    def create_file(self, filename):
        new_abs_path = os.path.join(self.abs_path, filename)
        if os.path.exists(new_abs_path):
            raise PathExists(new_abs_path)
        fp = file(new_abs_path, 'w')
        fp.close()
        return self.wiki.get(os.path.join(self.path, filename))

    def create_directory(self, name):
        new_abs_path = os.path.join(self.abs_path, name)
        if os.path.exists(new_abs_path):
            raise PathExists(new_abs_path)

        os.makedirs(new_abs_path)
        np = self.wiki.get(os.path.join(self.path, name))

        return np
