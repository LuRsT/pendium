import pendium
from pendium.filesystem import ( Wiki, PathNotFound, PathExists )
import unittest

class PendiumTestCase(unittest.TestCase):

    def setUp( self ):
        return

    def test_path_not_found( self ):
        w = Wiki('wiki')
        try:
            p = w.get('notafile.md')
        except PathNotFound, e:
            pass
        except Exception, e:
            self.fail( 'Unexpected exception thrown' )
        else:
            self.fail('ExpectedException not thrown')

    def test_is_file( self ):
        w = Wiki('wiki')
        try:
            p = w.get('test.md')
            assert True  == p.is_leaf
            assert False == p.is_node
            assert False == p.is_binary
        except Exception, e:
            self.fail( 'Unexpected exception thrown' )

    def test_is_dir( self ):
        w = Wiki('wiki')
        try:
            p = w.get('one_folder')
            assert False == p.is_leaf
            assert True  == p.is_node
        except Exception, e:
            self.fail( 'Unexpected exception thrown' )

    def test_create_file( self ):
        w = Wiki('wiki')
        try:
            p = w.get('one_folder')
            new_file = p.create_file( 'test_create.md' )
            assert True  == new_file.is_leaf
            assert False == new_file.is_node
            assert False == new_file.is_binary
        except PathExists:
            self.fail( 'File already exists' )
        except Exception, e:
            self.fail( 'Unexpected exception thrown' )

    def test_delete_file( self ):
        w = Wiki('wiki')
        try:
            p = w.get('one_folder/test_create.md')
            p.delete()
            w.get('one_folder/test_create.md')
        except PathNotFound:
            pass
        except Exception, e:
            self.fail( 'Unexpected exception thrown' )


    def tearDown( self ):
        return

if __name__ == '__main__':
    unittest.main()
