from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class ChipGravitySliderManager(Manager):
    s_puzzles = {}

    class Chip(object):
        def __init__(self, prototype, start, finish):
            self.prototype = prototype
            self.start = start
            self.finish = finish

    class Param(object):
        def __init__(self, MovieSlots, MovieSlotsStart, grid_size, ChipNumber, PrototypeBlock, prototype_arrow_up, prototype_arrow_down, prototype_arrow_left, prototype_arrow_right, chips):
            self.movie_slots = MovieSlots
            self.MovieSlotsStart = MovieSlotsStart
            self.grid_size = grid_size
            self.ChipNumber = ChipNumber
            self.PrototypeBlock = PrototypeBlock
            self.prototype_arrow_up = prototype_arrow_up
            self.prototype_arrow_down = prototype_arrow_down
            self.prototype_arrow_left = prototype_arrow_left
            self.prototype_arrow_right = prototype_arrow_right

            self.chips = chips

        def __repr__(self):
            return "<ChipGravitySliderManager.Param id={} MovieSlots={} GridSize={}>".format(id(self), self.movie_slots, self.grid_size)

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            EnigmaName = record.get("EnigmaName")
            Param = record.get("Param")
            MovieSlots = record.get("MovieSlots")
            MovieSlotsStart = record.get("MovieSlotsStart")
            GridWidth = record.get("GridWidth")
            GridHeight = record.get("GridHeight")
            ChipNumber = record.get("ChipNumber")
            PrototypeBlock = record.get("PrototypeBlock")
            PrototypeArrowUp = record.get("PrototypeArrowUp", None)
            PrototypeArrowDown = record.get("PrototypeArrowDown", None)
            PrototypeArrowLeft = record.get("PrototypeArrowLeft", None)
            PrototypeArrowRight = record.get("PrototypeArrowRight", None)

            result = ChipGravitySliderManager.addParam(EnigmaName, module, Param, MovieSlots, MovieSlotsStart, ChipNumber, GridWidth, GridHeight, PrototypeBlock, PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft, PrototypeArrowRight)

            if result is False:
                error_msg = "ChipGravitySliderManager invalid addParam {}".format(EnigmaName)
                Trace.log("Manager", 0, error_msg)
                return False

        return True

    @staticmethod
    def addParam(EnigmaName, Module, Param, MovieSlots, MovieSlotsStart, ChipNumber, GridWidth, GridHeight, PrototypeBlock, PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft, PrototypeArrowRight):
        if EnigmaName in ChipGravitySliderManager.s_puzzles:
            error_msg = "ChipGravitySliderManager already have param for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        # read Param Database
        records = DatabaseManager.getDatabaseRecords(Module, Param)

        if records is None:
            error_msg = "ChipGravitySliderManager cant find Param database for {}".format(EnigmaName)
            Trace.log("Manager", 0, error_msg)
            return False

        chips = []

        for record in records:
            ChipName = record.get("ChipName")
            StartPosition = record.get("StartPosition")
            FinishPosition = record.get("FinishPosition")

            chip_desc = ChipGravitySliderManager.Chip(ChipName, StartPosition, FinishPosition)

            chips.append(chip_desc)

        grid_size = (GridHeight, GridWidth)

        NewParam = ChipGravitySliderManager.Param(MovieSlots, MovieSlotsStart, grid_size, ChipNumber, PrototypeBlock, PrototypeArrowUp, PrototypeArrowDown, PrototypeArrowLeft, PrototypeArrowRight, chips)

        ChipGravitySliderManager.s_puzzles[EnigmaName] = NewParam
        return True

    @staticmethod
    def getParam(EnigmaName):
        return ChipGravitySliderManager.s_puzzles.get(EnigmaName)