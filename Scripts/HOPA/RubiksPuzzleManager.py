from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class RubiksPuzzleManager(Manager):
    s_puzzles = {}

    class RubiksPuzzleParam(object):
        def __init__(self, MovieSlots, PrototypeMovieChip1, PrototypeMovieChip2, VerticesDict, StartStateDict, WinStateDict):
            self.MovieSlots = MovieSlots

            self.PrototypeMovieChip1 = PrototypeMovieChip1
            self.PrototypeMovieChip2 = PrototypeMovieChip2

            self.VerticesDict = VerticesDict
            self.StartStateDict = StartStateDict
            self.WinStateDict = WinStateDict

        def getMovieSlotsName(self):
            return self.MovieSlots

        def getPrototypeMovieChip1(self):
            return self.PrototypeMovieChip1

        def getPrototypeMovieChip2(self):
            return self.PrototypeMovieChip2

        def isVertexAdjacentToVertex(self, vertex):
            adjacent_vertices = self.getAdjacentVerticesForVertex(vertex)

            if adjacent_vertices is None:
                return False

            return vertex in adjacent_vertices

        def getAdjacentVerticesForVertex(self, vertex):
            if vertex not in self.VerticesDict:
                return None

            return self.VerticesDict[vertex]

        def getStartState(self):
            return self.StartStateDict

        def isWinState(self, state):
            return state == self.WinStateDict

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")

            ParamGraph = record.get("ParamGraph")
            ParamStates = record.get("ParamStates")

            MovieSlots = record.get("MovieSlots")
            PrototypeMovieChip1 = record.get("PrototypeMovieChip1")
            PrototypeMovieChip2 = record.get("PrototypeMovieChip2")

            VertexSlotMask = record.get("VertexSlotMask", "")

            result = RubiksPuzzleManager.addParam(EnigmaName, module, ParamGraph, ParamStates, MovieSlots,
                                                  PrototypeMovieChip1, PrototypeMovieChip2, VertexSlotMask)

            if result is False:
                error_msg = "RubiksPuzzleManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, ParamGraph, ParamStates, MovieSlots, PrototypeMovieChip1, PrototypeMovieChip2, VertexSlotMask):
        if EnigmaName in RubiksPuzzleManager.s_puzzles:
            error_msg = "RubiksPuzzleManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Graph database
        records = DatabaseManager.getDatabaseRecords(Module, ParamGraph)

        if records is None:
            error_msg = "RubiksPuzzleManager cant find Graph database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        vertices_dict = {}

        for record in records:
            Vertex = record.get("Vertex")
            AdjacentVertices = record.get("AdjacentVertices")

            VertexWithMask = VertexSlotMask + str(Vertex)
            AdjacentVerticesWithMask = list(map(lambda VertexIndex: VertexSlotMask + str(VertexIndex), AdjacentVertices))

            vertices_dict[VertexWithMask] = AdjacentVerticesWithMask

        # read States database
        records = DatabaseManager.getDatabaseRecords(Module, ParamStates)

        if records is None:
            error_msg = "RubiksPuzzleManager cant find States database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        start_state_dict = {}
        win_state_dict = {}

        for record in records:
            Vertex = record.get("Vertex")
            StartState = record.get("StartState", 1)
            WinState = record.get("WinState", 1)

            VertexWithMask = VertexSlotMask + str(Vertex)

            start_state_dict[VertexWithMask] = StartState
            win_state_dict[VertexWithMask] = WinState

        NewParam = RubiksPuzzleManager.RubiksPuzzleParam(MovieSlots, PrototypeMovieChip1, PrototypeMovieChip2,
                                                         vertices_dict, start_state_dict, win_state_dict)

        RubiksPuzzleManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return RubiksPuzzleManager.s_puzzles.get(EnigmaName)
