from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class SwapAndRotateMovieChipsManager(Manager):
    s_puzzles = {}

    class SwapAndRotateMovieChipsParam(object):
        def __init__(self, MovieSlots, RotationSocket, RotationCount, RotationClockwise, ChipsDict, SlotsDict):
            self.MovieSlots = MovieSlots
            self.RotationButton = RotationSocket

            self.RotationCount = RotationCount
            self.RotationClockwise = RotationClockwise

            self.ChipsDict = {}
            self.SlotsDict = {}

            self.ChipsDict.update(ChipsDict)
            self.SlotsDict.update(SlotsDict)

        def getRotationAngle(self):
            RotationAngleDegrees = 360 / self.RotationCount
            RotationAngleDegrees *= -1 if self.RotationClockwise else 1

            PI = 3.141592653589793238

            RotationAngleRadians = RotationAngleDegrees * (PI / 180)

            return RotationAngleRadians

        def getMovieSlotsName(self):
            return self.MovieSlots

        def getSlots(self):
            return self.SlotsDict

        def getChips(self):
            return self.ChipsDict

    class ChipParam(object):
        def __init__(self, MovieIdle, MovieSelected):
            self.MovieIdle = MovieIdle
            self.MovieSelected = MovieSelected

    class SlotParam(object):
        def __init__(self, MovieSlot, MovieSocket):
            self.MovieSlot = MovieSlot
            self.MovieSocket = MovieSocket

            self.StartChipID = None
            self.EndChipID = None
            self.EndChipID2 = None

            self.StartChipRotation = 0
            self.EndChipRotation = 0
            self.EndChipRotation2 = 0

        def setStartChipID(self, ChipID):
            self.StartChipID = ChipID

        def setEndChipID(self, ChipID):
            self.EndChipID = ChipID

        def setEndChipID2(self, ChipID):
            self.EndChipID2 = ChipID

        def setStartChipRotation(self, Rotation):
            if Rotation is None:
                return

            self.StartChipRotation = Rotation

        def setEndChipRotation(self, Rotation):
            if Rotation is None:
                return

            self.EndChipRotation = Rotation

        def setEndChipRotation2(self, Rotation):
            if Rotation is None:
                return

            self.EndChipRotation2 = Rotation

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")

            MovieSlots = record.get("MovieSlots")
            RotationSocket = record.get("RotationButton")

            RotationCount = record.get("RotationCount", 2)
            RotationClockWise = bool(record.get("RotationClockwise", 1))

            ParamChips = record.get("ParamChips")
            ParamSlots = record.get("ParamSlots")
            ParamStates = record.get("ParamStates")

            result = SwapAndRotateMovieChipsManager.addParam(EnigmaName, module, MovieSlots, RotationSocket,
                                                             RotationCount, RotationClockWise, ParamChips, ParamSlots,
                                                             ParamStates)

            if result is False:
                error_msg = "SwapAndRotateMovieChipsManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, MovieSlots, RotationSocket, RotationCount, RotationClockwise, ParamChips,
                 ParamSlots, ParamStates):
        if EnigmaName in SwapAndRotateMovieChipsManager.s_puzzles:
            error_msg = "SwapAndRotateMovieChipsManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Chips database
        chip_records = DatabaseManager.getDatabaseRecords(Module, ParamChips)

        if chip_records is None:
            error_msg = "SwapAndRotateMovieChipsManager cant find Chips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        chips_dict = {}

        for chip_record in chip_records:
            ChipID = chip_record.get('ChipID')
            MovieIdle = chip_record.get('MovieIdle')
            MovieSelected = chip_record.get('MovieSelected')

            if ChipID in chips_dict:
                warning_msg = "SwapAndRotateMovieChipsManager in Chips database already exist chip with ID = {}".format(ChipID)
                Trace.log("Manager", 0, warning_msg)
                continue

            chips_dict[ChipID] = SwapAndRotateMovieChipsManager.ChipParam(MovieIdle, MovieSelected)

        # read Slots database
        slot_records = DatabaseManager.getDatabaseRecords(Module, ParamSlots)

        if slot_records is None:
            error_msg = "SwapAndRotateMovieChipsManager cant find Slots database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        slots_dict = {}

        for slot_record in slot_records:
            SlotID = slot_record.get('SlotID')
            MovieSlot = slot_record.get('MovieSlot')
            MovieSocket = slot_record.get('MovieSocket')

            if SlotID in slots_dict:
                warning_msg = "SwapAndRotateMovieChipsManager in Slots database already exist slot with ID = {}".format(SlotID)
                Trace.log("Manager", 0, warning_msg)
                continue

            slots_dict[SlotID] = SwapAndRotateMovieChipsManager.SlotParam(MovieSlot, MovieSocket)

        # read States database
        state_records = DatabaseManager.getDatabaseRecords(Module, ParamStates)

        if state_records is None:
            error_msg = "SwapAndRotateMovieChipsManager cant find States database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        for state_record in state_records:
            SlotID = state_record.get('SlotID')

            Slot = slots_dict.get(SlotID)

            if Slot is None:
                warning_msg = "SwapAndRotateMovieChipsManager in Slots database dont exist slot with ID = {}".format(SlotID)
                Trace.log("Manager", 0, warning_msg)
                continue

            StartChipID = state_record.get('StartChipID')

            if StartChipID not in chips_dict:
                warning_msg = "SwapAndRotateMovieChipsManager in Chips database dont exist chip with ID = {}".format(StartChipID)
                Trace.log("Manager", 0, warning_msg)
                continue

            Slot.setStartChipID(StartChipID)

            StartChipRotation = state_record.get('StartChipRotation', 0)
            Slot.setStartChipRotation(StartChipRotation)

            EndChipID = state_record.get('EndChipID')

            if EndChipID not in chips_dict:
                warning_msg = "SwapAndRotateMovieChipsManager in Chips database dont exist chip with ID = {}".format(EndChipID)
                Trace.log("Manager", 0, warning_msg)

            Slot.setEndChipID(EndChipID)

            EndChipRotation = state_record.get('EndChipRotation', 0)
            Slot.setEndChipRotation(EndChipRotation)

            # Extra params /////////////////////////////////////////////////////////////////////////////////////////////

            EndChipID2 = state_record.get('EndChipID2', None)

            if EndChipID2 is not None:
                Slot.setEndChipID2(EndChipID2)

                EndChipRotation2 = state_record.get('EndChipRotation2', 0)
                Slot.setEndChipRotation2(EndChipRotation2)

            # //////////////////////////////////////////////////////////////////////////////////////////////////////////

        NewParam = SwapAndRotateMovieChipsManager.SwapAndRotateMovieChipsParam(
            MovieSlots, RotationSocket, RotationCount, RotationClockwise, chips_dict, slots_dict)

        SwapAndRotateMovieChipsManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return SwapAndRotateMovieChipsManager.s_puzzles.get(EnigmaName)
