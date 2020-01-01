import markdown

from flask import Markup

from pendium.plugins import IRenderPlugin


class Markdown(IRenderPlugin):
    name = "Markdown"

    def __init__(self):
        super(Markdown, self).__init__()
        self.extensions = []

    def configure(self, configuration):
        self.extensions = configuration.get("extensions", [])

    def render(self, content):
        markdown_content = markdown.markdown(content)

        return Markup(markdown_content)
