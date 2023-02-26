from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class MoviePathChipTransporterManager(Manager):
    s_puzzles = {}

    class MoviePathChipTransporterParam(object):
        def __init__(self, MovieSlots, MovieChip, StartSlot, WinSlotsChain, SlotsDict, PathsDict, GraphDict):
            self.MovieSlots = MovieSlots
            self.MovieChip = MovieChip

            self.StartSlot = StartSlot
            self.WinSlotsChain = WinSlotsChain

            self.SlotsDict = SlotsDict
            self.PathsDict = PathsDict
            self.GraphDict = GraphDict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")

            ParamSlots = record.get("ParamSlots")
            ParamPaths = record.get("ParamPaths")
            ParamGraph = record.get("ParamGraph")

            MovieSlots = record.get("MovieSlots")

            MovieChip = record.get("MovieChip")

            StartSlot = record.get("StartSlot")
            WinSlotsChain = record.get("WinSlotsChain", [])

            result = MoviePathChipTransporterManager.addParam(EnigmaName, module, ParamSlots, ParamPaths, ParamGraph, MovieSlots, MovieChip, StartSlot, WinSlotsChain)

            if result is False:
                error_msg = "MoviePathChipTransporterManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamSlots, ParamPaths, ParamGraph, MovieSlots, MovieChip, StartSlot, WinSlotsChain):
        if EnigmaName in MoviePathChipTransporterManager.s_puzzles:
            error_msg = "MoviePathChipTransporterManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Slots database
        records = DatabaseManager.getDatabaseRecords(Module, ParamSlots)

        if records is None:
            error_msg = "MoviePathChipTransporterManager cant find Slots database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        slots_dict = {}

        for record in records:
            # SlotID, MovieSlot, MovieSocket
            SlotID = record.get('SlotID')
            MovieSlot = record.get('MovieSlot')
            MovieSocket = record.get('MovieSocket')
            MovieSelected = record.get('MovieSelected')

            slots_dict[SlotID] = (MovieSlot, MovieSocket, MovieSelected)

        # read Paths database
        records = DatabaseManager.getDatabaseRecords(Module, ParamPaths)

        if records is None:
            error_msg = "MoviePathChipTransporterManager cant find Paths database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        paths_dict = {}

        for record in records:
            # PathID, Movie
            PathID = record.get('PathID')
            Movie = record.get('Movie')

            paths_dict[PathID] = Movie

        # read Graph database
        records = DatabaseManager.getDatabaseRecords(Module, ParamGraph)

        if records is None:
            error_msg = "MoviePathChipTransporterManager cant find Graph database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        graph_dict = {}

        for record in records:
            # FromSlotID, ToSlotID, PathID
            FromSlotID = record.get('FromSlotID')
            ToSlotID = record.get('ToSlotID')
            PathID = record.get('PathID')

            graph_dict[(FromSlotID, ToSlotID)] = PathID

        NewParam = MoviePathChipTransporterManager.MoviePathChipTransporterParam(MovieSlots, MovieChip, StartSlot, WinSlotsChain, slots_dict, paths_dict, graph_dict)

        MoviePathChipTransporterManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return MoviePathChipTransporterManager.s_puzzles.get(EnigmaName)