import docutils.core
import docutils.io

from flask import Markup
from pendium.plugins import IRenderPlugin


class Rest(IRenderPlugin):
    name = "Rest"

    def render(self, content):
        content = docutils.core.publish_string(content,
                                            writer_name='html')
        return Markup(content)
