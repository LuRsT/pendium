from docutils.core import publish_string
from flask import Markup

from pendium.plugins import IRenderPlugin


class Rest(IRenderPlugin):
    name = 'Rest'

    def render(self, content):
        content = publish_string(content, writer_name='html')
        return Markup(content)
