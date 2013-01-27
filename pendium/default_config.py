# Flask config
DEBUG      = True
TESTING    = True
SECRET_KEY = 'pendiumissopendular'

# Pendium config
HOST_IP               = None
WIKI_EXTENSIONS       = { 'Markdown' : [ 'md', 'mdw' ],
                          'Text'     : [ 'txt' ],
                          'HTML'     : [ 'html', 'htm' ],
                          'Python'   : [ 'py'  ],
                          'Rest'     : [ 'rst' ]
                        }
WIKI_DEFAULT_RENDERER = None
WIKI_PLUGINS_CONFIG   = { "Markdown" : { 'extensions' : [ 'headerid', 'toc',
                                                          'tables', 'footnotes',
                                                          'fenced_code', 'codehilite'
                                                        ]
                                       },
                        }
WIKI_GIT_SUPPORT      = False

DEFAULT_HOME_FILE     = 'home.md'

CODEHILITE_STYLESHEET = 'plain.css'

BLACKLIST_EXTENSIONS  = [ ]
