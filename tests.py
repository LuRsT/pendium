import unittest

from flask import Markup
from pendium import app
from pendium.filesystem import Wiki, PathNotFound, PathExists, PathNotFound


class PendiumTestCase(unittest.TestCase):
    def setUp(self):
        self.test_filename = "test_pendium_file.md"
        app.config.from_object("pendium.default_config")
        config = app.config
        self.w = Wiki(
            config.get("WIKI_DIR", ""),
            extensions=config.get("WIKI_EXTENSIONS", {}),
            default_renderer=config.get("WIKI_DEFAULT_RENDERER", None),
            plugins_config=config.get("WIKI_PLUGINS_CONFIG", {}),
            has_vcs=False,
        )

        # Testing flask app
        self._app = app.test_client()

    def create_file(self):
        p = self.w.get("")
        new_file = p.create_file(self.test_filename)

        assert new_file.is_leaf is True
        assert new_file.is_node is False
        assert new_file.is_binary is False

    def edit_file(self):
        p = self.w.get(self.test_filename)
        p.content(content="#header")
        p.save()

        assert p.can_render is True
        self.assertEqual(p.render(), Markup('<h1>header</h1>'))
        assert p.content() == "#header"

    def is_file(self):
        p = self.w.get(self.test_filename)

        assert p.is_leaf is True
        assert p.is_node is False
        assert p.is_binary is False

    def delete_file(self):
        p = self.w.get(self.test_filename)
        p.delete()
        self.w.get(self.test_filename)

    # def test_filesystem(self):
    #     self.create_file()
    #     self.edit_file()
    #     self.is_file()
    #     self.delete_file()

    def test_is_dir(self):
        p = self.w.get("")
        assert p.is_leaf is False
        assert p.is_node is True
        assert len(p.items()) > 0

    def test_path_not_found(self):
        with self.assertRaises(PathNotFound):
            self.w.get("notafile.md")

    def test_views(self):
        rv = self._app.get("/")
        assert rv.data is not None

    def test_search(self):
        assert self.w.search("impossibru") == []
        # Simple search, should have some results, be sure to
        # have some files in the wiki folder
        assert len(self.w.search("#")) > 0


if __name__ == "__main__":
    unittest.main()
