from yapsy.IPlugin import IPlugin


class IPendiumPlugin(IPlugin):
    def configure(self, configuration):
        pass


class IRenderPlugin(IPendiumPlugin):
    pass
