from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ProgrammatorForFindWayMGManager(Manager):
    s_puzzles = {}

    class ProgrammatorForFindWayMGParam(object):
        def __init__(self, chipDict, ChipManMovieName, placeList, FinishCellID, FailCells, skipPosition):
            self.Chips = chipDict
            self.ChipManMovieName = ChipManMovieName
            self.PlacesName = placeList
            self.FinishCellID = FinishCellID
            self.FailCells = FailCells
            self.skipPosition = skipPosition

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            EnigmaName	ChipParam	ChipManMovieName	PlaceParam  FinishCellID    SkipPosition	[FailCells]
            '''
            EnigmaName = record.get('EnigmaName')
            ChipParam = record.get('ChipParam')
            ChipManMovieName = record.get('ChipManMovieName')
            PlaceParam = record.get('PlaceParam')
            FinishCellID = record.get('FinishCellID')
            FailCells = record.get('FailCells')
            SkipPosition = record.get('SkipPosition')

            result = ProgrammatorForFindWayMGManager.addParam(EnigmaName, module, ChipParam, ChipManMovieName,
                                                              PlaceParam, FinishCellID, FailCells, SkipPosition)
            if result is False:
                error_msg = "ProgrammatorForFindWayMGManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ChipParam, ChipManMovieName, PlaceParam, FinishCellID, FailCells, SkipPosition):
        if EnigmaName in ProgrammatorForFindWayMGManager.s_puzzles:
            error_msg = "ProgrammatorForFindWayMGManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChipParam)

        chipDict = {}

        if records is None:
            error_msg = "ProgrammatorForFindWayMGManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	MovieName	ChipPower
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')
            ChipPower = record.get('ChipPower')
            chipDict[ChipID] = (MovieName, ChipPower)
        # ==============================================================================================================

        # -------------- Place -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, PlaceParam)

        placeList = []

        if records is None:
            error_msg = "ProgrammatorForFindWayMGManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            PlaceName	Number
            '''
            PlaceName = record.get('PlaceName')
            Number = record.get('Number')
            placeList.append((PlaceName, Number))
        # ==============================================================================================================
        # -------------- SkipPosition ----------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, SkipPosition)

        skipPosition = {}

        if records is None:
            error_msg = "ProgrammatorForFindWayMGManager cant find SkipPosition database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	PlaceID
            '''
            ChipID = record.get('ChipID')
            PlaceID = record.get('PlaceID')
            skipPosition[ChipID] = PlaceID
        # ==============================================================================================================
        new_param = ProgrammatorForFindWayMGManager.ProgrammatorForFindWayMGParam(chipDict, ChipManMovieName, placeList,
                                                                                  FinishCellID, FailCells, skipPosition)
        ProgrammatorForFindWayMGManager.s_puzzles[EnigmaName] = new_param

    @staticmethod
    def getParam(EnigmaName):
        return ProgrammatorForFindWayMGManager.s_puzzles.get(EnigmaName)
