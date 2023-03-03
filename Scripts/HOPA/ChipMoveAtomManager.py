from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ChipMoveAtomManager(Manager):
    s_puzzles = {}

    class Slot(object):
        def __init__(self, slot_name, socket_name, start_chip_id, win_chip_id):
            self.slot_name = slot_name
            self.socket_name = socket_name
            self.start_chip_id = start_chip_id
            self.win_chip_id = win_chip_id

    class Chip(object):
        def __init__(self, chip_movie_name, glow_movie_name):
            self.chip_movie_name = chip_movie_name
            self.glow_movie_name = glow_movie_name

    class Path(object):
        def __init__(self, movie_path, tag):
            self.movie_path = movie_path
            self.tag = tag

    class Param(object):
        def __init__(self, MovieSlots, Slots, Chips, Paths, TypeMovie):
            self.MovieSlots = MovieSlots
            self.Slots = Slots
            self.Chips = Chips
            self.Paths = Paths
            self.TypeMovie = TypeMovie

        def getMovieSlots(self):
            return self.MovieSlots

        def getSlots(self):
            return self.Slots

        def getChips(self):
            return self.Chips

        def getPaths(self):
            return self.Paths

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")

            ParamSlotsAndChips = record.get("ParamSlotsAndChips")
            ParamPaths = record.get("ParamPaths")

            MovieSlots = record.get("MovieSlots")

            TypeMovie = record.get("TypeMovie", "Movie")

            result = ChipMoveAtomManager.addParam(EnigmaName, module, ParamSlotsAndChips, ParamPaths, MovieSlots, TypeMovie)

            if result is False:
                error_msg = "ChipMoveAtomManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamSlotsAndChips, ParamPaths, MovieSlots, TypeMovie):
        if EnigmaName in ChipMoveAtomManager.s_puzzles:
            error_msg = "ChipMoveAtomManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read SlotsAndChips database
        records = DatabaseManager.getDatabaseRecords(Module, ParamSlotsAndChips)

        if records is None:
            error_msg = "ChipMoveAtomManager cant find SlotsAndChips database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        slots_dict = {}
        chips_dict = {}

        for record in records:
            SlotID = record.get("SlotID")
            SlotName = record.get("SlotName")
            SocketName = record.get("SocketName")
            ChipID = record.get("ChipID")
            MovieChip = record.get("MovieChip")
            MovieGlow = record.get("MovieGlow")
            WinChipID = record.get("WinChipID")

            slots_dict[SlotID] = ChipMoveAtomManager.Slot(SlotName, SocketName, ChipID, WinChipID)
            chips_dict[ChipID] = ChipMoveAtomManager.Chip(MovieChip, MovieGlow)

        # read Paths database
        records = DatabaseManager.getDatabaseRecords(Module, ParamPaths)

        if records is None:
            error_msg = "ChipMoveAtomManager cant find Paths database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        paths_dict = {}

        for record in records:
            FromSlotID = record.get("FromSlotID")
            ToSlotID = record.get("ToSlotID")
            MoviePath = record.get("MoviePath")
            Tag = record.get("Tag")

            paths_dict[(FromSlotID, ToSlotID)] = ChipMoveAtomManager.Path(MoviePath, Tag)

        NewParam = ChipMoveAtomManager.Param(MovieSlots, slots_dict, chips_dict, paths_dict, TypeMovie)

        ChipMoveAtomManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChipMoveAtomManager.s_puzzles.get(EnigmaName)
