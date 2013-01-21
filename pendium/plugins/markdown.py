import markdown

from yapsy.IPlugin import IPlugin
from flask import Markup
from pendium.utils import load_config

class Markdown( IPlugin ):
    name       = "Markdown"
    extensions = [ 'md', 'mdw' ]

    def render( self, content ):
        markdown_content = markdown.markdown( content, [ 'headerid', 'toc',
                                                'tables', 'footnotes', 'codehilite' ] )

        return Markup( markdown_content )
