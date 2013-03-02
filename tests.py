from pendium import app
from pendium.filesystem import (Wiki, PathNotFound, PathExists)
import unittest


class PendiumTestCase(unittest.TestCase):
    def setUp(self):
        config = app.config
        self.w = Wiki(config['WIKI_DIR'],
                      extensions       = config.get('WIKI_EXTENSIONS', {}),
                      default_renderer = config.get('WIKI_DEFAULT_RENDERER', None),
                      plugins_config   = config.get('WIKI_PLUGINS_CONFIG', {}),
                      git_support      = config.get('WIKI_GIT_SUPPORT', False))

        return

    def test_1_create_file(self):
        try:
            p = self.w.get('')
            new_file = p.create_file('test_create.md')
            assert new_file.is_leaf is True
            assert new_file.is_node is False
            assert new_file.is_binary is False
        except PathExists:
            self.fail('File already exists')
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_2_edit(self):
        try:
            p = self.w.get('test_create.md')
            p.content('#header')
            p.save()
            assert p.can_render is True
            assert p.render() == '<h1 id="header">header</h1>'
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_3_is_file(self):
        try:
            p = self.w.get('test_create.md')
            assert p.is_leaf is True
            assert p.is_node is False
            assert p.is_binary is False
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_4_delete_file(self):
        try:
            p = self.w.get('test_create.md')
            p.delete()
            self.w.get('test_create.md')
        except PathNotFound:
            pass
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_is_dir(self):
        try:
            p = self.w.get('')
            assert p.is_leaf is False
            assert p.is_node is True
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_path_not_found(self):
        try:
            self.w.get('notafile.md')
        except PathNotFound:
            pass
        except Exception:
            self.fail('Unexpected exception thrown')
        else:
            self.fail('ExpectedException not thrown')

    def tearDown(self):
        return

if __name__ == '__main__':
    unittest.main()
