import docutils.core
import docutils.io

from flask import Markup
from pendium.plugins import IRenderPlugin


class Rest( IRenderPlugin ):
    name = "Rest"

    def render( self, text ):
        text = docutils.core.publish_string( text,
                                             writer_name='html')
        return Markup(text)
