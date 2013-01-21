# Flask config
DEBUG      = True
TESTING    = True
SECRET_KEY = 'pendiumissopendular'

# Pendium config
HOST_IP               = None
WIKI_EXTENSIONS       = { 'Markdown' : ['md', 'mdw'],
                          'Text' : ['txt'],
                          'HTML' : ['html']
                        }
WIKI_DEFAULT_RENDERER = None 
WIKI_MARKDOWN_PLUGINS = [ 'headerid', 'toc', 
                          'tables', 'footnotes', 'codehilite' 
                        ]
WIKI_GIT_SUPPORT      = False
