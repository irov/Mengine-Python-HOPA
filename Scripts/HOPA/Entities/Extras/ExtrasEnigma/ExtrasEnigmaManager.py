from Foundation.DatabaseManager import DatabaseManager


class ExtrasEnigmaManager(object):
    s_data = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            name = record.get("Name")
            collection = record.get("Collection")

            data = ExtrasEnigmaManager.loadCollection(module, collection)

            ExtrasEnigmaManager.s_data[name] = data
            pass
        pass

    @staticmethod
    def loadCollection(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        collection = {}

        for record in records:
            spriteName = record.get("SpriteName")
            EnigmaName = record.get("EnigmaName")
            SceneName = record.get("SceneName")

            collection[spriteName] = (EnigmaName, SceneName)
            pass

        return collection
        pass

    @staticmethod
    def getData(name):
        if ExtrasEnigmaManager.hasData(name) is False:
            Trace.log("Manager", 0, "ExtrasEnigmaManager.getData  invalid name%s" % (name))
            return None
            pass
        data = ExtrasEnigmaManager.s_data[name]
        return data
        pass

    @staticmethod
    def hasData(name):
        if name in ExtrasEnigmaManager.s_data.keys():
            return True
            pass
        return False
        pass

    pass
