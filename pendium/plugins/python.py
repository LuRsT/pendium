from flask import Markup
from pendium.plugins import IRenderPlugin

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


class Python(IRenderPlugin):
    name = "Python"

    def render(self, content):
        return Markup(highlight(content, PythonLexer(), HtmlFormatter()))
