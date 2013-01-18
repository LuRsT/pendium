# Flask config
DEBUG      = True
TESTING    = True
SECRET_KEY = 'pendiumissopendular'

# Pendium config
HOST_IP               = None 
WIKI_EXTENSIONS       = { 'markdown' : ['md', 'mdw'],
                          'text' : ['txt'],
                          'html' : ['html']
                        }  
WIKI_DEFAULT_RENDERER = None 
WIKI_MARKDOWN_PLUGINS = [ 'headerid', 'toc', 
                          'tables', 'footnotes', 'codehilite' 
                        ]
WIKI_GIT_SUPPORT      = False
