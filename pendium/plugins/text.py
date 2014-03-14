from flask import Markup, escape

from pendium.plugins import IRenderPlugin


class Text(IRenderPlugin):
    name = 'Text'

    def render(self, content):
        return Markup('<pre>%s</pre>' % escape(content))
