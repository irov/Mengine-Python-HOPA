from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class ChipDragDropOnRightPlaceManager(Manager):
    s_puzzles = {}

    class ChipDragDropOnRightPlaceParam(object):
        def __init__(self, chipDict, combsDict):
            self.Chips = chipDict
            self.Combs = combsDict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	ChipsParam	CombsParam
            '''
            EnigmaName = record.get('EnigmaName')
            ChipsParam = record.get('ChipsParam')
            CombsParam = record.get('CombsParam')

            result = ChipDragDropOnRightPlaceManager.addParam(EnigmaName, module, ChipsParam, CombsParam)

            if result is False:
                error_msg = "ChipDragDropOnRightPlaceManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
            return True

    @staticmethod
    def addParam(EnigmaName, Module, ChipsParam, CombsParam):
        if EnigmaName in ChipDragDropOnRightPlaceManager.s_puzzles:
            error_msg = "ChipDragDropOnRightPlaceManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChipsParam)
        chipDict = {}
        if records is None:
            error_msg = "ChipDragDropOnRightPlaceManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID MovieName
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')

            chipDict[ChipID] = MovieName
        # ==============================================================================================================

        # -------------- Combs -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, CombsParam)
        combsDict = {}
        if records is None:
            error_msg = "ChipDragDropOnRightPlaceManager cant find Combs database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	StartPlaceID	FinishPlaceID
            '''
            ChipID = record.get('ChipID')
            StartPlaceID = record.get('StartPlaceID')
            FinishPlaceID = record.get('FinishPlaceID')

            combsDict[ChipID] = (StartPlaceID, FinishPlaceID)
        # ==============================================================================================================

        new_param = ChipDragDropOnRightPlaceManager.ChipDragDropOnRightPlaceParam(chipDict, combsDict)
        ChipDragDropOnRightPlaceManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChipDragDropOnRightPlaceManager.s_puzzles.get(EnigmaName)