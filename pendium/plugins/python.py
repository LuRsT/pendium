from flask import Markup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from pendium.plugins import IRenderPlugin


class Python(IRenderPlugin):
    name = "Python"

    def render(self, content):
        return Markup(highlight(content, PythonLexer(), HtmlFormatter()))
