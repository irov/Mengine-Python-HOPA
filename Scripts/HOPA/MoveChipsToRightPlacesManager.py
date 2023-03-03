from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class MoveChipsToRightPlacesManager(Manager):
    s_puzzles = {}

    class MoveChipsToRightPlacesParam(object):
        def __init__(self, chip_dict):
            self.chipDict = chip_dict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            '''
                EnigmaName, ParamChips
            '''
            EnigmaName = record.get('EnigmaName')
            ParamChips = record.get('ParamChips')

            result = MoveChipsToRightPlacesManager.addParam(EnigmaName, module, ParamChips)

            if result is False:
                error_msg = "MoveChipsToRightPlacesManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamChips):
        if EnigmaName in MoveChipsToRightPlacesManager.s_puzzles:
            error_msg = "MoveChipsToRightPlacesManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamChips)
        chip_dict = {}
        if records is None:
            error_msg = "MoveChipsToRightPlacesManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID, MovieName
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')
            chip_dict[ChipID] = MovieName
        # ==============================================================================================================
        new_param = MoveChipsToRightPlacesManager.MoveChipsToRightPlacesParam(chip_dict)

        MoveChipsToRightPlacesManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return MoveChipsToRightPlacesManager.s_puzzles.get(EnigmaName)
