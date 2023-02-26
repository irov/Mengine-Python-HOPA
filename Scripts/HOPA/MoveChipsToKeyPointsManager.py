from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class MoveChipsToKeyPointsManager(Manager):
    s_puzzles = {}

    class MoveChipsToKeyPointsParam(object):
        def __init__(self, chipParam, slotParam, WinParam):
            self.Slots = slotParam
            self.Chips = chipParam
            self.WinParam = WinParam

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName	ChipParam	SlotParam	WinParam

            '''
            EnigmaName = record.get('EnigmaName')
            ChipParam = record.get('ChipParam')
            SlotParam = record.get('SlotParam')
            WinParam = record.get('WinParam')

            result = MoveChipsToKeyPointsManager.addParam(EnigmaName, module, ChipParam, SlotParam, WinParam)

            if result is False:
                error_msg = "MoveChipsToKeyPointsManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ChipParam, SlotParam, WinParam):
        if EnigmaName in MoveChipsToKeyPointsManager.s_puzzles:
            error_msg = "MoveChipsToKeyPointsManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ChipParam)
        chipParam = {}
        if records is None:
            error_msg = "MoveChipsToKeyPointsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	MovieName
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')

            chipParam[ChipID] = MovieName

            pass
        # ==============================================================================================================

        # -------------- Slot ------------------------------------------------------------------------------------------

        records = DatabaseManager.getDatabaseRecords(Module, SlotParam)
        slotParam = {}
        if records is None:
            error_msg = "MoveChipsToKeyPointsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                slotID	SlotName	StartChip

            '''
            slotID = record.get('slotID')
            SlotName = record.get('SlotName')
            StartChip = record.get('StartChip')

            slotParam[slotID] = (SlotName, StartChip)

            pass
        # ==============================================================================================================

        # -------------- WinParam --------------------------------------------------------------------------------------

        records = DatabaseManager.getDatabaseRecords(Module, WinParam)
        WinParam = {}
        if records is None:
            error_msg = "MoveChipsToKeyPointsManager cant find WinParam database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                ChipID	FinishSlotID
            '''
            ChipID = record.get('ChipID')
            FinishSlotID = record.get('FinishSlotID')
            WinParam[ChipID] = FinishSlotID

            pass
        # ==============================================================================================================

        new_param = MoveChipsToKeyPointsManager.MoveChipsToKeyPointsParam(chipParam, slotParam, WinParam)

        MoveChipsToKeyPointsManager.s_puzzles[EnigmaName] = new_param

        return True

    @staticmethod
    def getParam(EnigmaName):
        return MoveChipsToKeyPointsManager.s_puzzles.get(EnigmaName)