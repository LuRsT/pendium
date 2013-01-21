from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from flask import Markup

from pendium.plugins import IRenderPlugin

class Pygmentizer( IRenderPlugin ):
    name = "Python"

    def render( self, text ):
        return Markup ( highlight(text, PythonLexer(), HtmlFormatter() ) )
