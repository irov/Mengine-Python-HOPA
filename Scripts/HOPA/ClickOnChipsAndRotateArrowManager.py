from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ClickOnChipsAndRotateArrowManager(Manager):
    s_puzzles = {}

    class ClickOnChipsAndRotateArrowParam(object):
        def __init__(self, chip_dict, winsComb, arrowParam):
            self.Chips = chip_dict
            self.winsComb = winsComb
            self.Arrow = arrowParam

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	ChipParam	WinsParam   ArrowParam

            '''
            EnigmaName = record.get('EnigmaName')
            ChipParam = record.get('ChipParam')
            ArrowParam = record.get('ArrowParam')
            WinsParam = record.get('WinsParam')

            result = ClickOnChipsAndRotateArrowManager.addParam(EnigmaName, module, ChipParam, ArrowParam, WinsParam)
            if result is False:
                error_msg = "ClickOnChipsAndRotateArrowManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ChipParam, ArrowParam, WinsParam):
        if EnigmaName in ClickOnChipsAndRotateArrowManager.s_puzzles:
            error_msg = "ClickOnChipsAndRotateArrowManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChipParam)
        chip_dict = {}
        if records is None:
            error_msg = "ClickOnChipsAndRotateArrowManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	CommonState	FailState	RightState
            '''
            ChipID = record.get('ChipID')
            CommonState = record.get('CommonState')
            FailState = record.get('FailState')
            RightState = record.get('RightState')

            chip_dict[ChipID] = (CommonState, FailState, RightState)
        # ==============================================================================================================

        # -------------- WinsComb --------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, WinsParam)
        winsComb = []
        if records is None:
            error_msg = "ClickOnChipsAndRotateArrowManager cant find WinsComb database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                WinsComb
            '''
            winsComb = record.get('WinsComb')
        # ==============================================================================================================

        # -------------- ArrowParam ------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ArrowParam)
        arrowParam = {}
        if records is None:
            error_msg = "ClickOnChipsAndRotateArrowManager cant find arrowParam database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                MovieName	StartPosition

            '''
            MovieName = record.get('MovieName')
            StartPosition = record.get('StartPosition')
            arrowParam[MovieName] = StartPosition
        # ==============================================================================================================

        new_param = ClickOnChipsAndRotateArrowManager.ClickOnChipsAndRotateArrowParam(chip_dict, winsComb, arrowParam)

        ClickOnChipsAndRotateArrowManager.s_puzzles[EnigmaName] = new_param

    @staticmethod
    def getParam(EnigmaName):
        return ClickOnChipsAndRotateArrowManager.s_puzzles.get(EnigmaName)
