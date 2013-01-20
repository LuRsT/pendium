from yapsy.IPlugin import IPlugin
from flask import Markup, escape

class Text( IPlugin ):
    name       = "Text"
    extensions = [ 'txt' ]

    def render( self, content ):
        return Markup( "<pre>%s</pre>" % escape( content ) )
