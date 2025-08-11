from Foundation.Manager import Manager

class OptionsMoreManager(Manager):
    s_options = {}

    @staticmethod
    def _onFinalize():
        OptionsMoreManager.s_options = {}
        pass

    @staticmethod
    def loadParams(module, param):
        return True
