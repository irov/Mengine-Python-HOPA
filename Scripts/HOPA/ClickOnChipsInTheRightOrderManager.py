from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ClickOnChipsInTheRightOrderManager(Manager):
    s_puzzles = {}

    class ClickOnChipsInTheRightOrderParam(object):
        def __init__(self, chip_dict, slot_dict, comb):
            self.chipDict = chip_dict
            self.slotDict = slot_dict
            self.comb = comb

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
                EnigmaName, ParamChips, ParamSlots, Combs, RightOrderMovie
            '''
            EnigmaName = record.get('EnigmaName')
            ParamChips = record.get('ParamChips')
            ParamSlots = record.get('ParamSlots')
            Combs = record.get('Combs')

            result = ClickOnChipsInTheRightOrderManager.addParam(EnigmaName, module, ParamChips, ParamSlots, Combs)

            if result is False:
                error_msg = "ClickOnChipsInTheRightOrderManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamChips, ParamSlots, Combs):
        if EnigmaName in ClickOnChipsInTheRightOrderManager.s_puzzles:
            error_msg = "ClickOnChipsInTheRightOrderManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamChips)
        chip_dict = {}
        if records is None:
            error_msg = "ClickOnChipsInTheRightOrderManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                SlotID, MovieName
            '''
            SlotID = record.get('SlotID')
            MovieName = record.get('MovieName')
            chip_dict[SlotID] = MovieName
        # ==============================================================================================================

        # -------------- Slots -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamSlots)
        slot_dict = {}
        if records is None:
            error_msg = "ClickOnChipsInTheRightOrderManager cant find Slots database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                SlotID, MovieName
            '''
            SlotID = record.get('SlotID')
            MovieName = record.get('MovieName')
            slot_dict[SlotID] = MovieName
        # ==============================================================================================================

        # -------------- winCombs --------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, Combs)

        comb = {}
        if records is None:
            error_msg = "ClickOnChipsInTheRightOrderManager cant find Slots database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                winsCombID, [WinCombs]

            '''
            winsCombID = record.get('winsCombID')
            winCombs = record.get('WinCombs')
            comb[winsCombID] = winCombs
        # ==============================================================================================================

        new_param = ClickOnChipsInTheRightOrderManager.ClickOnChipsInTheRightOrderParam(chip_dict, slot_dict, comb)

        ClickOnChipsInTheRightOrderManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ClickOnChipsInTheRightOrderManager.s_puzzles.get(EnigmaName)
