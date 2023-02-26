from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class MouseMagnetManager(Manager):
    s_puzzles = {}

    class Param(object):
        def __init__(self, PrototypeChip, PrototypeWalls, WallSocketName, WallNumber, ChipStartX, ChipStartY, FinishSocket):
            self.PrototypeChip = PrototypeChip
            self.PrototypeWalls = PrototypeWalls
            self.WallSocketName = WallSocketName
            self.WallNumber = WallNumber
            self.ChipStartX = ChipStartX
            self.ChipStartY = ChipStartY
            self.FinishSocket = FinishSocket
        def __repr__(self):
            return "<MouseMagnetManager.Param error"

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            PrototypeChip = record.get("PrototypeChip")
            PrototypeWalls = record.get("PrototypeWalls")
            WallSocketName = record.get("WallSocketName")
            WallNumber = record.get("WallNumber")
            ChipStartX = record.get("ChipStartX")
            ChipStartY = record.get("ChipStartY")
            FinishSocket = record.get("FinishSocket")

            result = MouseMagnetManager.addParam(EnigmaName, module, param, PrototypeChip, PrototypeWalls, WallSocketName, WallNumber, ChipStartX, ChipStartY, FinishSocket)

            if result is False:
                error_msg = "MouseMagnetManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, Param, PrototypeChip, PrototypeWalls, WallSocketName, WallNumber, ChipStartX, ChipStartY, FinishSocket):
        if EnigmaName in MouseMagnetManager.s_puzzles:
            error_msg = "MouseMagnetManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(Module, Param)

        NewParam = MouseMagnetManager.Param(PrototypeChip, PrototypeWalls, WallSocketName, WallNumber, ChipStartX, ChipStartY, FinishSocket)
        MouseMagnetManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return MouseMagnetManager.s_puzzles.get(EnigmaName)