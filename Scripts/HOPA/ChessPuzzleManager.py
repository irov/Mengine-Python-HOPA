from Foundation.Manager import Manager
from Foundation.DatabaseManager import DatabaseManager

class ChessPuzzleManager(Manager):
    s_games = {}

    class ChessPuzzleMovieGridDescription(object):
        def __init__(self, width, height, objectName):
            self.width = width
            self.height = height
            self.objectName = objectName
            self.cells = []
            pass

        def appendCells(self, cell):
            self.cells.append(cell)
            pass

    class ChessPuzzleGame(object):
        def __init__(self, grid, shifts, figures, targets):
            self.grid = grid
            self.shifts = shifts
            self.figures = figures
            self.targets = targets
            pass

    @staticmethod
    def _onInitialize():
        return True

    @staticmethod
    def _onFinalize():
        ChessPuzzleManager.s_games = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            CellsParam = record.get("Cells")
            GridParam = record.get("Grid")
            FiguresParam = record.get("Figures")
            TargetsParam = record.get("Targets")
            ShiftsParam = record.get("Shifts")

            ChessPuzzleManager.loadGame(Name, CellsParam, GridParam, FiguresParam, TargetsParam, ShiftsParam)
            pass
        pass

    @staticmethod
    def loadGame(module, name, cellsParam, gridParam, figuresParam, targetsParam, shiftsParam):
        grid = ChessPuzzleManager.loadGameGrid(module, gridParam)
        ChessPuzzleManager.loadGameCells(module, cellsParam, grid)
        shifts = ChessPuzzleManager.loadGameShifts(module, shiftsParam)
        figures = ChessPuzzleManager.loadGameFigures(module, figuresParam)
        targets = ChessPuzzleManager.loadGameTargets(module, targetsParam)

        game = ChessPuzzleManager.ChessPuzzleGame(grid, shifts, figures, targets)
        ChessPuzzleManager.s_games[name] = game
        return game
        pass

    @staticmethod
    def loadGameGrid(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        record = records[0]

        Width = record.get("Width")
        Height = record.get("Height")
        ObjectName = record.get("ObjectName")
        grid = ChessPuzzleManager.ChessPuzzleMovieGridDescription(Width, Height, ObjectName)
        return grid
        pass

    @staticmethod
    def loadGameCells(module, param, grid):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            X = record.get("X")
            Y = record.get("Y")
            SlotName = record.get("SlotName")

            cells = dict(x=X, y=Y, slotName=SlotName)

            grid.appendCells(cells)
            pass
        pass

    @staticmethod
    def loadGameShifts(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        shifts = {}
        for record in records:
            ShiftId = record.get("ShiftId")
            X = record.get("X")
            Y = record.get("Y")
            DX = record.get("DX")
            DY = record.get("DY")
            Prototype = record.get("Prototype")
            shifts[ShiftId] = dict(x=X, y=Y, dX=DX, dY=DY, prototype=Prototype)
            pass
        return shifts

    @staticmethod
    def loadGameFigures(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        figures = {}
        for record in records:
            FigureId = record.get("FigureId")
            X = record.get("X")
            Y = record.get("Y")
            FigureType = record.get("FigureType")
            Prototype = record.get("Prototype")
            figures[FigureId] = dict(x=X, y=Y, figureType=FigureType, prototype=Prototype)
            pass
        return figures

    @staticmethod
    def loadGameTargets(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        targets = {}
        for record in records:
            TargetId = record.get("TargetId")
            X = record.get("X")
            Y = record.get("Y")
            FigureType = record.get("FigureType")
            Prototype = record.get("Prototype")
            targets[TargetId] = dict(x=X, y=Y, figureType=FigureType, prototype=Prototype)
            pass
        return targets

    @staticmethod
    def getGame(name):
        if name not in ChessPuzzleManager.s_games:
            Trace.log("Manager", 0, "PathChipsManager.getGame: not found game %s" % (name))
            return None
        game = ChessPuzzleManager.s_games[name]
        return game

    @staticmethod
    def hasGame(name):
        return name in ChessPuzzleManager.s_games
