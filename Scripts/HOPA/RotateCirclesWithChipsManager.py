from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class RotateCirclesWithChipsManager(Manager):
    # print '=========================Manager RotateCirclesWithChips==============================='
    s_puzzles = {}

    class RotateCirclesWithChipsParam(object):
        def __init__(self, chips_dict, circles_dict, winsComb_dict, startComb_dict, SlotsParam):
            self.chips_dict = chips_dict
            self.circles_dict = circles_dict
            self.winsComb_dict = winsComb_dict
            self.startComb_dict = startComb_dict
            self.slots_dict = SlotsParam

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get('EnigmaName')
            ParamChips = record.get('ParamChips')
            ParamCircles = record.get('ParamCircles')
            WinsComb = record.get('WinsComb')
            StartComb = record.get('StartComb')
            ParamSlots = record.get('ParamSlots')

            result = RotateCirclesWithChipsManager.addParam(EnigmaName, module, ParamChips, ParamCircles,
                                                            WinsComb, StartComb, ParamSlots)

            if result is False:
                error_msg = "RotateCirclesWithChipsManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamChips, ParamCircles, WinsComb, StartComb, ParamSlots):
        if EnigmaName in RotateCirclesWithChipsManager.s_puzzles:
            error_msg = "RotateCirclesWithChipsManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamChips)
        chips_dict = {}
        if records is None:
            error_msg = "RotateCirclesWithChipsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	MovieName
            '''
            ChipID = record.get('ChipID')
            MovieName = record.get('MovieName')

            chips_dict[ChipID] = MovieName
        # ==============================================================================================================

        # -------------- Circles ---------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamCircles)
        circles_dict = {}
        if records is None:
            error_msg = "RotateCirclesWithChipsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            CircleID	MovieName	NumberOfSlotsForChips
            '''
            CircleID = record.get('CircleID')
            MovieName = record.get('MovieName')
            NumberOfSlotsForChips = record.get('NumberOfSlotsForChips')

            circles_dict[CircleID] = (MovieName, NumberOfSlotsForChips)
        # ==============================================================================================================

        # -------------- startComb -------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, StartComb)
        startComb_dict = {}
        if records is None:
            error_msg = "RotateCirclesWithChipsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            chipID circleID	slotID onCenter	
            '''
            ChipID = record.get('ChipID')
            CircleID = record.get('CircleID')
            SlotID = record.get('SlotID')
            onCenter = record.get('onCenter')

            startComb_dict[ChipID] = (CircleID, onCenter, SlotID)
        # ==============================================================================================================

        # -------------- winsComb --------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, WinsComb)
        winsComb_dict = {}
        if records is None:
            error_msg = "RotateCirclesWithChipsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            ChipID	CircleID	onCenter SlotID

            '''
            ChipID = record.get('ChipID')
            CircleID = record.get('CircleID')
            SlotID = record.get('SlotID')
            onCenter = record.get('onCenter')

            winsComb_dict[ChipID] = (CircleID, onCenter, SlotID)
        # ==============================================================================================================

        # -------------- SlotsParam ------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamSlots)
        slots_dict = {}
        if records is None:
            error_msg = "RotateCirclesWithChipsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
            circleID	slotID	onCenter

            '''
            slotID = record.get('slotID')
            onCenter = record.get('onCenter')
            circleID = record.get('circleID')

            slots_dict[(circleID, slotID)] = onCenter
        # ==============================================================================================================

        new_param = RotateCirclesWithChipsManager.RotateCirclesWithChipsParam(chips_dict, circles_dict, winsComb_dict,
                                                                              startComb_dict, slots_dict)

        RotateCirclesWithChipsManager.s_puzzles[EnigmaName] = new_param

        return True

    @staticmethod
    def getParam(EnigmaName):
        return RotateCirclesWithChipsManager.s_puzzles.get(EnigmaName)
