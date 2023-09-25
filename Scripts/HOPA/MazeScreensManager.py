from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class MazeScreensManager(Manager):

    s_params = {}

    class Param(object):     # todo
        def __init__(self, name):
            self.EnigmaName = name

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record["EnigmaName"]

            result = MazeScreensManager.loadParam(module, EnigmaName, record)

            if result is False:
                Trace.log("Manager", 0, "MazeScreensManager fail to load params for {!r}".format(EnigmaName))
                return False

        return True

    @staticmethod
    def loadParam(module, enigma_name, record):     # todo
        param = MazeScreensManager.Param(enigma_name)

        MazeScreensManager.s_params[enigma_name] = param

        return True

    @staticmethod
    def getParams(enigma_name):
        return MazeScreensManager.s_params.get(enigma_name)
