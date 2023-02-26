from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.Manager import Manager

class SwapChipsWithDifferentSlotTypesParam(object):
    def __init__(self, MovieSlots, ChipsDict, SlotsDict, FixedSlotsIDs, DragDrop, PlaySwapSoundTwice, SaveMG, PlaySkip, ChipMoveTimeOverride, LitChips, LitAlpha, LitTime):
        self.MovieSlots = MovieSlots

        self.ChipsDict = {}
        self.SlotsDict = {}

        self.ChipsDict.update(ChipsDict)
        self.SlotsDict.update(SlotsDict)

        self.FixedSlotsIDs = FixedSlotsIDs

        self.DragDrop = DragDrop
        self.PlaySwapSoundTwice = PlaySwapSoundTwice

        self.SaveMG = SaveMG
        self.PlaySkip = PlaySkip

        if ChipMoveTimeOverride > 0:
            self.ChipMoveTime = ChipMoveTimeOverride
        else:
            self.ChipMoveTime = DefaultManager.getDefaultFloat('SwapChipsWithDifferentSlotTypesTime', 400.0)

        self.LitChips = LitChips
        self.LitAlpha = LitAlpha
        self.LitTime = LitTime

    def getMovieSlotsName(self):
        return self.MovieSlots

    def getSlots(self):
        return self.SlotsDict

    def getChips(self):
        return self.ChipsDict

class ChipParam(object):
    def __init__(self, Type, MovieNotPlaced, MoviePlaced, MovieSelected):
        self.Type = Type
        self.MovieNotPlaced = MovieNotPlaced
        self.MoviePlaced = MoviePlaced
        self.MovieSelected = MovieSelected

class SlotParam(object):
    def __init__(self, MovieSlot, MovieSocket, SupportedChipTypes, AllowedSlots):
        self.MovieSlot = MovieSlot
        self.MovieSocket = MovieSocket
        self.SupportedChipTypes = SupportedChipTypes
        self.AllowedSlots = AllowedSlots

        self.StartChipID = None
        self.EndChipIDs = []

    def setStartChipID(self, ChipID):
        self.StartChipID = ChipID

    def setEndChipIDs(self, ChipIDs):
        self.EndChipIDs = ChipIDs

class SwapChipsWithDifferentSlotTypesManager(Manager):
    s_puzzles = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            """
            EnigmaName	MovieSlots	ParamChips	ParamSlots	
            ParamStates	DragDrop [FixedSlotsIDs]
            """
            EnigmaName = record.get("EnigmaName")

            MovieSlots = record.get("MovieSlots")

            ParamChips = record.get("ParamChips")
            ParamSlots = record.get("ParamSlots")
            ParamStates = record.get("ParamStates")

            FixedSlotsIDs = record.get("FixedSlotsIDs", [])

            DragDrop = bool(record.get("DragDrop", False))
            PlaySwapSoundTwice = bool(record.get("PlaySwapSoundTwice", True))
            SaveMG = bool(record.get("SaveMG", False))
            PlaySkip = bool(record.get("PlaySkip", True))
            ChipMoveTimeOverride = record.get("ChipMoveTimeOverride", 0.0)
            LitChips = bool(record.get("LitChips", False))
            LitAlpha = record.get("LitAlpha", 0.0)
            LitTime = record.get("LitTime", 0.0)

            result = SwapChipsWithDifferentSlotTypesManager.addParam(EnigmaName, module, MovieSlots, ParamChips, ParamSlots, ParamStates, FixedSlotsIDs, DragDrop, PlaySwapSoundTwice, SaveMG, PlaySkip, ChipMoveTimeOverride, LitChips, LitAlpha, LitTime)

            if result is False:
                error_msg = "SwapChipsWithDifferentSlotTypesManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, MovieSlots, ParamChips, ParamSlots, ParamStates, FixedSlotsIDs, DragDrop, PlaySwapSoundTwice, SaveMG, PlaySkip, ChipMoveTimeOverride, LitChips, LitAlpha, LitTime):
        if EnigmaName in SwapChipsWithDifferentSlotTypesManager.s_puzzles:
            error_msg = "SwapChipsWithDifferentSlotTypesManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Chips database
        chip_records = DatabaseManager.getDatabaseRecords(Module, ParamChips)

        if chip_records is None:
            error_msg = "SwapChipsWithDifferentSlotTypesManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        chips_dict = {}

        for chip_record in chip_records:
            """
            ChipID	Type	MovieNotPlaced	MoviePlaced	MovieSelected
            """
            ChipID = chip_record.get('ChipID')
            Type = chip_record.get('Type')
            MovieNotPlaced = chip_record.get('MovieNotPlaced')
            MoviePlaced = chip_record.get('MoviePlaced')
            MovieSelected = chip_record.get('MovieSelected')

            if ChipID in chips_dict:
                warning_msg = "SwapChipsWithDifferentSlotTypesManager in" \
                              " Chips database already exist chip with ID = {}".format(ChipID)
                Trace.log("Manager", 0, warning_msg)
                continue

            chips_dict[ChipID] = ChipParam(Type, MovieNotPlaced, MoviePlaced, MovieSelected)

        # read Slots database
        slot_records = DatabaseManager.getDatabaseRecords(Module, ParamSlots)

        if slot_records is None:
            error_msg = "SwapChipsWithDifferentSlotTypesManager cant find Slots database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        slots_dict = {}

        for slot_record in slot_records:
            """
            MovieSocket	[SupportedChipTypes]
            """
            SlotID = slot_record.get('SlotID')
            MovieSlot = slot_record.get('MovieSlot')
            MovieSocket = slot_record.get('MovieSocket')
            SupportedChipTypes = slot_record.get('SupportedChipTypes')
            AllowedSlots = slot_record.get('AllowedSlotsID', [])

            if SlotID in slots_dict:
                warning_msg = "SwapChipsWithDifferentSlotTypesManager in Slots " \
                              "database already exist slot with ID = {}".format(SlotID)
                Trace.log("Manager", 0, warning_msg)
                continue

            slots_dict[SlotID] = SlotParam(MovieSlot, MovieSocket, SupportedChipTypes, AllowedSlots)

        # read States database
        state_records = DatabaseManager.getDatabaseRecords(Module, ParamStates)

        if state_records is None:
            error_msg = "SwapChipsWithDifferentSlotTypesManager cant find States database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for state_record in state_records:
            """
            SlotID	StartChipID	[EndChipIDs]
            """
            SlotID = state_record.get('SlotID')

            Slot = slots_dict.get(SlotID)

            if Slot is None:
                warning_msg = "SwapChipsWithDifferentSlotTypesManager " \
                              "in Slots database dont exist slot with ID = {}".format(SlotID)
                Trace.log("Manager", 0, warning_msg)
                continue

            StartChipID = state_record.get('StartChipID')

            if StartChipID is not None and StartChipID not in chips_dict:
                warning_msg = "SwapChipsWithDifferentSlotTypesManager " \
                              "in Chips database dont exist chip with ID = {}".format(StartChipID)
                Trace.log("Manager", 0, warning_msg)
                continue

            Slot.setStartChipID(StartChipID)

            EndChipIDs = state_record.get('EndChipIDs', [])

            for EndChipID in EndChipIDs:
                if EndChipID not in chips_dict:
                    warning_msg = "SwapChipsWithDifferentSlotTypesManager in " \
                                  "Chips database dont exist chip with ID = {}".format(EndChipID)
                    Trace.log("Manager", 0, warning_msg)

            Slot.setEndChipIDs(EndChipIDs)

        NewParam = SwapChipsWithDifferentSlotTypesParam(MovieSlots, chips_dict, slots_dict, FixedSlotsIDs, DragDrop, PlaySwapSoundTwice, SaveMG, PlaySkip, ChipMoveTimeOverride, LitChips, LitAlpha, LitTime)

        SwapChipsWithDifferentSlotTypesManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return SwapChipsWithDifferentSlotTypesManager.s_puzzles.get(EnigmaName)