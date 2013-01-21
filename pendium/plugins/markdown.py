import markdown

from flask import Markup
from pendium.utils import load_config
from pendium.plugins import IRenderPlugin 

class Markdown( IRenderPlugin ):
    name       = "Markdown"

    def render( self, content ):
        markdown_content = markdown.markdown( content, [ 'headerid', 'toc',
                                                'tables', 'footnotes', 'codehilite' ] )

        return Markup( markdown_content )
