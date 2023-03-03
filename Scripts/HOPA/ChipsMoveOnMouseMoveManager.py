from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ChipsMoveOnMouseMoveManager(Manager):
    s_puzzles = {}

    class Param(object):
        def __init__(self, MovieBG, Bugs, Layers):
            self.MovieBG = MovieBG
            self.Bugs = Bugs
            self.Layers = Layers

        def __repr__(self):
            return "<ChipsMoveOnMouseMoveManager.Param id={}".format(id(self))

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            Param = record.get("Param")
            MovieBG = record.get("MovieBG")

            result = ChipsMoveOnMouseMoveManager.addParam(EnigmaName, module, Param, MovieBG)

            if result is False:
                error_msg = "ChipsMoveOnMouseMoveManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, Param, MovieBG):
        if EnigmaName in ChipsMoveOnMouseMoveManager.s_puzzles:
            error_msg = "ChipsMoveOnMouseMoveManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(Module, Param)

        if records is None:
            error_msg = "ChipsMoveOnMouseMoveManager cant find Param database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        Bugs = []
        Layers = []

        for record in records:
            Prototype = record.get("Prototype")
            LayerName = record.get("LayerName")

            Bugs.append(Prototype)
            Layers.append(LayerName)

        NewParam = ChipsMoveOnMouseMoveManager.Param(MovieBG, Bugs, Layers)

        ChipsMoveOnMouseMoveManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChipsMoveOnMouseMoveManager.s_puzzles.get(EnigmaName)
