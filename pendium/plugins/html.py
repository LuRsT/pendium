from pendium.plugins import IRenderPlugin

class HTML( IRenderPlugin ):
    name       = "HTML"

    def render( self, content ):
        return content
