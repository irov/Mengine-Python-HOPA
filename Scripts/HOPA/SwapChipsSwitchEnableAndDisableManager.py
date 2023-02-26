from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class SwapChipsSwitchEnableAndDisableManager(Manager):
    s_puzzles = {}

    class SwapChipsSwitchEnableAndDisableParam(object):
        def __init__(self, red_dict, blue_dict, green_dict, black_dict, blueSelected_dict, redSelected_dict, greenSelected_dict, blackSelected_dict, slot_dict, startComb_dict):
            self.redDict = red_dict
            self.blueDict = blue_dict
            self.greenDict = green_dict
            self.blackDict = black_dict
            self.blueSelectedDict = blueSelected_dict
            self.redSelectedDict = redSelected_dict
            self.greenSelectedDict = greenSelected_dict
            self.blackSelectedDict = blackSelected_dict
            self.slotDict = slot_dict
            self.startCombDict = startComb_dict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get('EnigmaName')
            ParamChips = record.get('ParamChips')
            ParamSlots = record.get('ParamSlots')
            ParamStartComb = record.get('ParamStartComb')

            result = SwapChipsSwitchEnableAndDisableManager.addParam(EnigmaName, module, ParamChips, ParamSlots, ParamStartComb)

            if result is False:
                error_msg = "SwapChipsSwitchEnableAndDisableManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamChips, ParamSlots, ParamStartComb):
        if EnigmaName in SwapChipsSwitchEnableAndDisableManager.s_puzzles:
            error_msg = "SwapChipsSwitchEnableAndDisableManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # -------------- Chips -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamChips)
        red_dict = {}
        blue_dict = {}
        green_dict = {}
        black_dict = {}
        blueSelected_dict = {}
        redSelected_dict = {}
        greenSelected_dict = {}
        blackSelected_dict = {}

        if records is None:
            error_msg = "SwapChipsSwitchEnableAndDisableManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                SlotID, Blue, Red, Green, Black, BlueSelected, RedSelected, GreenSelected, BlackSelected
            '''
            SlotID = record.get('SlotID')
            Blue = record.get('Blue')
            Red = record.get('Red')
            Green = record.get('Green')
            Black = record.get('Black')
            BlueSelected = record.get('BlueSelected')
            RedSelected = record.get('RedSelected')
            GreenSelected = record.get('GreenSelected')
            BlackSelected = record.get('BlackSelected')

            red_dict[SlotID] = Red
            blue_dict[SlotID] = Blue
            green_dict[SlotID] = Green
            black_dict[SlotID] = Black
            blueSelected_dict[SlotID] = BlueSelected
            redSelected_dict[SlotID] = RedSelected
            greenSelected_dict[SlotID] = GreenSelected
            blackSelected_dict[SlotID] = BlackSelected

        # ==============================================================================================================

        # -------------- Slots -----------------------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamSlots)
        slot_dict = {}

        if records is None:
            error_msg = "SwapChipsSwitchEnableAndDisableManager cant find Chips database for {}".format(EnigmaName)
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

        # -------------- Start Combination -----------------------------------------------------------------------------
        records = DatabaseManager.getDatabaseRecords(Module, ParamStartComb)
        startComb_dict = {}

        if records is None:
            error_msg = "SwapChipsSwitchEnableAndDisableManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for record in records:
            '''
                SlotID, Type
            '''
            SlotID = record.get('SlotID')
            Type = record.get('Type')

            startComb_dict[SlotID] = Type
        # ==============================================================================================================

        new_param = SwapChipsSwitchEnableAndDisableManager.SwapChipsSwitchEnableAndDisableParam(red_dict, blue_dict, green_dict, black_dict, blueSelected_dict, redSelected_dict, greenSelected_dict, blackSelected_dict, slot_dict, startComb_dict)
        SwapChipsSwitchEnableAndDisableManager.s_puzzles[EnigmaName] = new_param
        return True

    @staticmethod
    def getParam(EnigmaName):
        return SwapChipsSwitchEnableAndDisableManager.s_puzzles.get(EnigmaName)