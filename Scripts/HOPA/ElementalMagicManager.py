from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager


class ElementalMagicManager(Manager):
    class Params(object):
        if _DEVELOPMENT:
            def __repr__(self):
                return "<{}: {}>".format(self.__class__.__name__, self.__dict__)

    class ConfigParams(Params):
        def __init__(self, records):
            pass

    class ElementsParams(Params):
        def __init__(self, records):
            pass

    class MacroUsageParams(Params):
        def __init__(self, records):
            pass

    class MoviesParams(Params):
        def __init__(self, records):
            pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)
        # for record in records:

        return True
