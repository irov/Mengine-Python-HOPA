from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class SwitchWayDirectionPuzzleManager(Manager):
    s_puzzles = {}

    class SwitchWayDirectionPuzzleParam(object):
        def __init__(self, MovieMain, SlotsDict, GraphDict, scaledSprites):
            self.MovieMain = MovieMain

            self.SlotsDict = SlotsDict
            self.GraphDict = GraphDict
            self.scaledSprites = scaledSprites

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")

            MovieMain = record.get("MovieMain")

            ParamSlots = record.get("ParamSlots")
            ParamGraph = record.get("ParamGraph")

            result = SwitchWayDirectionPuzzleManager.addParam(EnigmaName, module, MovieMain, ParamSlots, ParamGraph)

            if result is False:
                error_msg = "SwitchWayDirectionPuzzleManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, MovieMain, ParamSlots, ParamGraph):
        if EnigmaName in SwitchWayDirectionPuzzleManager.s_puzzles:
            error_msg = "SwitchWayDirectionPuzzleManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Slots database
        records = DatabaseManager.getDatabaseRecords(Module, ParamSlots)

        if records is None:
            error_msg = "SwitchWayDirectionPuzzleManager cant find Slots database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        slots_dict = {}
        scaledSprites = []
        for record in records:
            # SlotID, MovieSlot, MovieSocket
            SlotID = record.get('SlotID')

            SocketName = record.get('SocketName')
            SubMovieWin = record.get('SubMovieWin')
            WinCount = record.get('WinCount')
            ScaledSprites = record.get('ScaledSprites')
            scaledSprites.append(ScaledSprites)
            slots_dict[SlotID] = (SocketName, SubMovieWin, WinCount)

        # read Graph database
        records = DatabaseManager.getDatabaseRecords(Module, ParamGraph)

        if records is None:
            error_msg = "SwitchWayDirectionPuzzleManager cant find Graph database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        graph_dict = {}

        for record in records:
            # FromSlotID, ToSlotID, PathID
            FromSlotID = record.get('FromSlotID')
            ToSlotID = record.get('ToSlotID')
            SubMoviePath = record.get('SubMoviePath')
            StartState = bool(record.get('StartState'))

            graph_dict[(FromSlotID, ToSlotID)] = (SubMoviePath, StartState)

        NewParam = SwitchWayDirectionPuzzleManager.SwitchWayDirectionPuzzleParam(MovieMain, slots_dict, graph_dict, scaledSprites)

        SwitchWayDirectionPuzzleManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return SwitchWayDirectionPuzzleManager.s_puzzles.get(EnigmaName)
