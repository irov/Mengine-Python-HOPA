from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class BoardCell(object):
    Passage = "."
    Wall = "X"
    Start = "S"
    Finish = "F"
    Gate = "G"
    Lever = "L"


class ChangeScreenOnClickManager(Manager):
    s_puzzles = {}

    class Param(object):
        def __init__(self, MapName, HandName, PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft,
                     PrototypeArrowRight, StateNames, EnvironmentNames, Board, GateCloseNames, GateOpenNames, LeverNames):
            self.MapName = MapName
            self.HandName = HandName
            # map
            self.StateNames = StateNames
            self.EnvironmentNames = EnvironmentNames
            self.Board = Board
            self.GateCloseNames = GateCloseNames
            self.GateOpenNames = GateOpenNames
            self.LeverNames = LeverNames
            # arrows
            self.PrototypeArrowUp = PrototypeArrowUp
            self.PrototypeArrowDown = PrototypeArrowDown
            self.PrototypeArrowLeft = PrototypeArrowLeft
            self.PrototypeArrowRight = PrototypeArrowRight

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record["EnigmaName"]
            Param = record["Param"]
            ParamGraph = record["ParamGraph"]
            MapName = record.get("MapName", None)
            HandName = record.get("HandName", None)
            PrototypeArrowUp = record["PrototypeArrowUp"]
            PrototypeArrowDown = record["PrototypeArrowDown"]
            PrototypeArrowLeft = record["PrototypeArrowLeft"]
            PrototypeArrowRight = record["PrototypeArrowRight"]

            result = ChangeScreenOnClickManager.addParam(EnigmaName, module, Param, ParamGraph, MapName, HandName,
                                                         PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft,
                                                         PrototypeArrowRight)

            if result is False:
                error_msg = "ChangeScreenOnClickManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, Param, ParamGraph, MapName, HandName,
                 PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft, PrototypeArrowRight):

        if EnigmaName in ChangeScreenOnClickManager.s_puzzles:
            error_msg = "ChangeScreenOnClickManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # --- setup movie params

        records_Movie = DatabaseManager.getDatabaseRecords(Module, Param)

        if records_Movie is None:
            error_msg = "ChangeScreenOnClickManager cant find Param database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        StateNames = []
        EnvironmentNames = []
        GateOpenNames = []
        GateCloseNames = []
        LeverNames = []

        for record in records_Movie:
            StateName = record.get("StateName", None)
            EnvironmentName = record.get("EnvironmentName", None)
            GateOpenName = record.get("GateOpenName", None)
            GateCloseName = record.get("GateCloseName", None)
            LeverName = record.get("LeverName", None)

            if StateName is not None:
                StateNames.append(StateName)
            if EnvironmentName is not None:
                EnvironmentNames.append(EnvironmentName)
            if GateOpenName is not None:
                GateOpenNames.append(GateOpenName)
            if GateCloseName is not None:
                GateCloseNames.append(GateCloseName)
            if LeverName is not None:
                LeverNames.append(LeverName)

        if _DEVELOPMENT is True:
            if len(GateOpenNames) != len(GateCloseNames) != len(LeverNames):
                Trace.log("Manager", 0, "ChangeScreenOnClickManager size of GateNames != LeverNames")
                return False
            if len(StateNames) != 6:
                Trace.log("Manager", 0, "ChangeScreenOnClickManager size of StateNames != 6")
                return False
            if len(EnvironmentNames) == 0:
                Trace.log("Manager", 0, "ChangeScreenOnClickManager add at least one EnvironmentName")
                return False

        # --- setup graph params

        records_Graph = DatabaseManager.getDatabaseRecords(Module, ParamGraph)

        Board = []

        for record in records_Graph:
            row = record.get("row")
            Values = record.get("Values", [])

            if _DEVELOPMENT:
                _error = False
                for value in Values:
                    if value[0] not in [BoardCell.Gate, BoardCell.Lever]:
                        continue
                    target_number = value[1:]
                    if len(target_number) == 0:
                        Trace.log("Manager", 0, "ChangeScreenOnClick number is empty in {!r} at {}".format(value, row))
                        _error = True
                    if target_number.isdigit() is False:
                        Trace.log("Manager", 0, "ChangeScreenOnClick invalid number in {!r} at {}".format(value, row))
                        _error = True
                if _error is True:
                    return False

            Board.append(Values)

        # --- save param

        NewParam = ChangeScreenOnClickManager.Param(MapName, HandName, PrototypeArrowUp, PrototypeArrowDown,
                                                    PrototypeArrowLeft, PrototypeArrowRight, StateNames,
                                                    EnvironmentNames, Board, GateCloseNames, GateOpenNames, LeverNames)

        ChangeScreenOnClickManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChangeScreenOnClickManager.s_puzzles.get(EnigmaName)
