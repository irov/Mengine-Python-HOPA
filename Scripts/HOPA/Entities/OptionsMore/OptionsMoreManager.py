class OptionsMoreManager(object):
    s_options = {}

    @staticmethod
    def onFinalize():
        OptionsMoreManager.s_options = {}
        pass

    @staticmethod
    def loadParams(module, param):
        return True
        pass
    pass