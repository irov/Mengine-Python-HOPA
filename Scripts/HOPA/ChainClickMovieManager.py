from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ChainClickMovieManager(Manager):
    s_puzzles = {}

    class Param(object):
        def __init__(self, MovieSlots, Slots, Repit, Chain):
            self.MovieSlots = MovieSlots
            self.Slots = Slots
            self.Chain = Chain
            self.Repit = Repit

        def getMovieSlotsName(self):
            return self.MovieSlots

        def getSlots(self):
            return self.Slots

        def getChain(self):
            return self.Chain

    class Slot(object):
        def __init__(self, Socket, MovieChipIdle, MovieChipSelected, MovieChipFail):
            self.Socket = Socket
            self.MovieChipIdle = MovieChipIdle
            self.MovieChipSelected = MovieChipSelected
            self.MovieChipFail = MovieChipFail

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        def getRightChain(chain_list):
            """ [1, '2, 7', 8] turns into [1, [2, 7], 8] """
            chain = []
            for id_ in chain_list:
                if isinstance(id_, str):
                    id_ = [int(i) for i in id_.split(", ")]
                chain.append(id_)
            return chain

        for record in records:
            EnigmaName = record.get("EnigmaName")

            Param = record.get("Param")
            MovieSlots = record.get("MovieSlots")
            Chain = getRightChain(record.get("Chain"))
            Repit = bool(record.get("Repetitions", 0))

            result = ChainClickMovieManager.addParam(EnigmaName, module, Param, MovieSlots, Repit, Chain)

            if result is False:
                error_msg = "ChainClickMovieManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, Param, MovieSlots, Repit, Chain):
        if EnigmaName in ChainClickMovieManager.s_puzzles:
            error_msg = "ChainClickMovieManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Param Database
        records = DatabaseManager.getDatabaseRecords(Module, Param)

        if records is None:
            error_msg = "ChainClickMovieManager cant find Param database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        slots_dict = {}

        for record in records:
            SlotID = record.get("SlotID")

            if SlotID in slots_dict:
                warning_msg = "ChainClickMovieManager in Param database already exist slot with ID = {}".format(SlotID)
                Trace.log("Manager", 0, warning_msg)
                continue

            Socket = record.get("Socket")
            MovieChipIdle = record.get("MovieChipIdle")
            MovieChipSelected = record.get("MovieChipSelected")
            MovieChipFail = record.get("MovieChipFail")

            slots_dict[SlotID] = ChainClickMovieManager.Slot(Socket, MovieChipIdle, MovieChipSelected, MovieChipFail)

        NewParam = ChainClickMovieManager.Param(MovieSlots, slots_dict, Repit, Chain)

        ChainClickMovieManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChainClickMovieManager.s_puzzles.get(EnigmaName)
