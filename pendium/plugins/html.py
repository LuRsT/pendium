from yapsy.IPlugin import IPlugin

class HTML( IPlugin ):
    name       = "HTML"
    extensions = [ 'html' ]

    def render( self, content ):
        return content
