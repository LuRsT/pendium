from yapsy.IPlugin import IPlugin
import re

class IPendiumPlugin( IPlugin ):
    def configure( self, configuration ):
        pass

class ISearchPlugin( IPendiumPlugin ):
    def search(self, wiki, term):
        #TODO: Decompose term into regex
        regex = re.compile(term, re.I)

        return self.dosearch(wiki, term, regex)

class IRenderPlugin( IPendiumPlugin ):
    pass
