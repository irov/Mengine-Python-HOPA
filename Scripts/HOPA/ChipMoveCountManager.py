from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class ChipMoveCountManager(Manager):
    s_puzzles = {}

    class CounterDesc(object):
        def __init__(self, prototype, max_number):
            self.prototype = prototype
            self.max_number = max_number

    class ChipDesc(object):
        def __init__(self, prototype, grid, finish, start, counter):
            self.prototype = prototype
            self.grid = grid
            self.finish = finish
            self.start = start
            self.counter = counter

    class Param(object):
        def __init__(self, movie_slots, grid_size, prototype_arrow_up, prototype_arrow_down, prototype_arrow_left,
                     prototype_arrow_right, chips):
            self.movie_slots = movie_slots
            self.grid_size = grid_size
            self.prototype_arrow_up = prototype_arrow_up
            self.prototype_arrow_down = prototype_arrow_down
            self.prototype_arrow_left = prototype_arrow_left
            self.prototype_arrow_right = prototype_arrow_right

            self.chips = chips

        def __repr__(self):
            return "<ChipMoveCountManager.Param id={} MovieSlots={} GridSize={}>".format(id(self), self.movie_slots, self.grid_size)

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            Param = record.get("Param")
            MovieSlots = record.get("MovieSlots")
            GridWidth = record.get("GridWidth")
            GridHeight = record.get("GridHeight")
            PrototypeArrowUp = record.get("PrototypeArrowUp")
            PrototypeArrowDown = record.get("PrototypeArrowDown")
            PrototypeArrowLeft = record.get("PrototypeArrowLeft")
            PrototypeArrowRight = record.get("PrototypeArrowRight")

            result = ChipMoveCountManager.addParam(EnigmaName, module, Param, MovieSlots, GridWidth, GridHeight,
                                                   PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft,
                                                   PrototypeArrowRight)

            if result is False:
                error_msg = "ChipMoveCountManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, Param, MovieSlots, GridWidth, GridHeight, PrototypeArrowUp, PrototypeArrowDown,
                 PrototypeArrowLeft, PrototypeArrowRight):
        if EnigmaName in ChipMoveCountManager.s_puzzles:
            error_msg = "ChipMoveCountManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Param Database
        records = DatabaseManager.getDatabaseRecords(Module, Param)

        if records is None:
            error_msg = "ChipMoveCountManager cant find Param database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        chips = []

        for record in records:
            PrototypeChip = record.get("PrototypeChip")

            GridFromRow = record.get("GridFromRow")
            GridFromCol = record.get("GridFromCol")
            GridToRow = record.get("GridToRow")
            GridToCol = record.get("GridToCol")

            grid = ((GridFromRow, GridFromCol), (GridToRow, GridToCol))

            FinishRow = record.get("FinishRow")
            FinishCol = record.get("FinishCol")

            finish = (FinishRow, FinishCol)

            PrototypeCount = record.get("PrototypeCount")
            Count = record.get("Count")

            StartRow = record.get("StartRow")
            StartCol = record.get("StartCol")

            start = (StartRow, StartCol)

            counter_desc = ChipMoveCountManager.CounterDesc(PrototypeCount, Count)
            chip_desc = ChipMoveCountManager.ChipDesc(PrototypeChip, grid, finish, start, counter_desc)

            chips.append(chip_desc)

        grid_size = (GridWidth, GridHeight)

        NewParam = ChipMoveCountManager.Param(MovieSlots, grid_size, PrototypeArrowUp, PrototypeArrowDown,
                                              PrototypeArrowLeft, PrototypeArrowRight, chips)

        ChipMoveCountManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChipMoveCountManager.s_puzzles.get(EnigmaName)
