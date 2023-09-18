from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ChangeScreenOnClickManager(Manager):
    s_puzzles = {}

    class BoardCell(object):
        TYPE_PASSAGE = "."
        TYPE_WALL = "X"
        TYPE_START = "S"
        TYPE_FINISH = "F"

    class Param(object):
        def __init__(self, MapName, HandName, PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft,
                     PrototypeArrowRight, StateNames, EnvironmentNames, Directions, Board):
            self.MapName = MapName
            self.HandName = HandName
            self.StateNames = StateNames
            self.EnvironmentNames = EnvironmentNames
            self.Directions = Directions
            self.Board = Board
            self.PrototypeArrowUp = PrototypeArrowUp
            self.PrototypeArrowDown = PrototypeArrowDown
            self.PrototypeArrowLeft = PrototypeArrowLeft
            self.PrototypeArrowRight = PrototypeArrowRight

        def __repr__(self):
            return "<ChangeScreenOnClickManager.Param id={}>".format(id(self))

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            Param = record.get("Param")
            ParamGraph = record.get("ParamGraph")
            MapName = record.get("MapName", None)
            HandName = record.get("HandName", None)
            PrototypeArrowUp = record.get("PrototypeArrowUp", None)
            PrototypeArrowDown = record.get("PrototypeArrowDown", None)
            PrototypeArrowLeft = record.get("PrototypeArrowLeft", None)
            PrototypeArrowRight = record.get("PrototypeArrowRight", None)

            result = ChangeScreenOnClickManager.addParam(EnigmaName, module, Param, ParamGraph, MapName, HandName,
                                                         PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft,
                                                         PrototypeArrowRight)

            if result is False:
                error_msg = "ChangeScreenOnClickManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, Param, ParamGraph, MapName, HandName, PrototypeArrowUp, PrototypeArrowDown,
                 PrototypeArrowLeft, PrototypeArrowRight):
        if EnigmaName in ChangeScreenOnClickManager.s_puzzles:
            error_msg = "ChangeScreenOnClickManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        records_Movie = DatabaseManager.getDatabaseRecords(Module, Param)

        if records_Movie is None:
            error_msg = "ChangeScreenOnClickManager cant find Param database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        StateNames = []
        EnvironmentNames = []

        for record in records_Movie:
            StateName = record.get("StateName", None)
            EnvironmentName = record.get("EnvironmentName", None)

            if StateName is not None:
                StateNames.append(StateName)
            if EnvironmentName is not None:
                EnvironmentNames.append(EnvironmentName)

        records_Graph = DatabaseManager.getDatabaseRecords(Module, ParamGraph)

        Directions = []
        Board = []

        for record in records_Graph:
            row = record.get("row")
            Values = record.get("Values", [])
            Board.append(Values)

        NewParam = ChangeScreenOnClickManager.Param(MapName, HandName, PrototypeArrowUp, PrototypeArrowDown,
                                                    PrototypeArrowLeft, PrototypeArrowRight, StateNames,
                                                    EnvironmentNames, Directions, Board)

        ChangeScreenOnClickManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChangeScreenOnClickManager.s_puzzles.get(EnigmaName)
