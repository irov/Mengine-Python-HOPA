from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager


class ElementalMagicManager(Manager):
    __PARAMS_TABLE_NAMES = {
        "config": "ElementalMagic_Config",
        "elements": "ElementalMagic_Elements",
        "macro_usage": "ElementalMagic_MacroUsage",
        "movies": "ElementalMagic_Movies",
    }

    s_configs = {}
    s_elements = {}
    s_macro_usages = {}
    s_movies = {}

    class Params(object):
        if _DEVELOPMENT:
            def __repr__(self):
                return "<{}: {}>".format(self.__class__.__name__, self.__dict__)

    class ConfigParams(Params):
        def __init__(self, records):
            self.config = {}

            for record in records:
                key = record.get("Key")
                value = record.get("Value")

                if key is not None:
                    self.config[key] = value

    class ElementsParams(Params):
        def __init__(self, record):
            self.element = ElementalMagicManager.getRecordValue(record, "Element")

    class MacroUsageParams(Params):
        def __init__(self, record):
            self.elemental_magic_id = ElementalMagicManager.getRecordValue(record, "ElementalMagic_ID")
            self.element = ElementalMagicManager.getRecordValue(record, "Element")
            self.limited = ElementalMagicManager.getRecordValue(record, "Limited")

    class MoviesParams(Params):
        def __init__(self, record):
            self.element = ElementalMagicManager.getRecordValue(record, "Element")
            self.movie2_appear = ElementalMagicManager.getRecordValue(record, "Movie2_Appear")
            self.movie2_idle = ElementalMagicManager.getRecordValue(record, "Movie2_Idle")
            self.movie2_use = ElementalMagicManager.getRecordValue(record, "Movie2_Use")
            self.movie2_disappear = ElementalMagicManager.getRecordValue(record, "Movie2_Disappear")

    @staticmethod
    def loadConfig(records):
        params = ElementalMagicManager.ConfigParams(records)
        ElementalMagicManager.s_configs = params.config

    @staticmethod
    def loadElements(records):
        for record in records:
            param = ElementalMagicManager.ElementsParams(record)
            if param.element is not None:
                ElementalMagicManager.s_elements[param.element] = param

    @staticmethod
    def loadMacroUsage(records):
        for record in records:
            param = ElementalMagicManager.MacroUsageParams(record)
            if param.elemental_magic_id is not None:
                ElementalMagicManager.s_macro_usages[param.elemental_magic_id] = param

    @staticmethod
    def loadMovies(records):
        for record in records:
            param = ElementalMagicManager.MoviesParams(record)
            if param.element is not None:
                ElementalMagicManager.s_movies[param.element] = param

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        if name == ElementalMagicManager.__PARAMS_TABLE_NAMES["config"]:
            ElementalMagicManager.loadConfig(records)
            print(ElementalMagicManager.s_configs)

        if name == ElementalMagicManager.__PARAMS_TABLE_NAMES["elements"]:
            ElementalMagicManager.loadElements(records)
            print(ElementalMagicManager.s_elements)

        if name == ElementalMagicManager.__PARAMS_TABLE_NAMES["macro_usage"]:
            ElementalMagicManager.loadMacroUsage(records)
            print(ElementalMagicManager.s_macro_usages)

        if name == ElementalMagicManager.__PARAMS_TABLE_NAMES["movies"]:
            ElementalMagicManager.loadMovies(records)
            print(ElementalMagicManager.s_movies)

        return True
