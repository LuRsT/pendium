from pendium.filesystem import (Wiki, PathNotFound, PathExists)
import unittest


class PendiumTestCase(unittest.TestCase):

    def setUp(self):
        return

    def test_path_not_found(self):
        w = Wiki('wiki')
        try:
            w.get('notafile.md')
        except PathNotFound:
            pass
        except Exception:
            self.fail('Unexpected exception thrown')
        else:
            self.fail('ExpectedException not thrown')

    def test_is_file(self):
        w = Wiki('wiki')
        try:
            p = w.get('test.md')
            assert p.is_leaf is True
            assert p.is_node is False
            assert p.is_binary is False
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_is_dir(self):
        w = Wiki('wiki')
        try:
            p = w.get('')
            assert p.is_leaf is False
            assert p.is_node is True
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_create_file(self):
        w = Wiki('wiki')
        try:
            p = w.get('')
            new_file = p.create_file('test_create.md')
            assert new_file.is_leaf is True
            assert new_file.is_node is False
            assert new_file.is_binary is False
        except PathExists:
            self.fail('File already exists')
        except Exception:
            self.fail('Unexpected exception thrown')

    def test_delete_file(self):
        w = Wiki('wiki')
        try:
            p = w.get('test_create.md')
            p.delete()
            w.get('test_create.md')
        except PathNotFound:
            pass
        except Exception:
            self.fail('Unexpected exception thrown')

    def tearDown(self):
        return

if __name__ == '__main__':
    unittest.main()
