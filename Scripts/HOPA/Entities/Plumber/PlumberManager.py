from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from HOPA.EnigmaManager import EnigmaManager

class PlumberManager(Manager):
    s_objects = {}

    class Plumber(object):
        def __init__(self, metric, cellMetric, fieldData, itemData, cellItemData, movementMovies, wallsData, buttons):
            self.metric = metric
            self.cellMetric = cellMetric
            self.fieldData = fieldData
            self.itemData = itemData
            self.cellItemData = cellItemData
            self.movementMovies = movementMovies
            self.wallsData = wallsData
            self.buttons = buttons
            pass

        def getButtons(self):
            return self.buttons

        def getWallsData(self):
            return self.wallsData

        def getMetric(self):
            return self.metric

        def getCellMetric(self):
            return self.cellMetric

        def getFieldData(self):
            return self.fieldData

        def getItemData(self):
            return self.itemData

        def getCellItemData(self):
            return self.cellItemData

        def getMovementMovies(self):
            return self.movementMovies

    class CellItem(object):
        def __init__(self, movie, movieSelected, directionMovieNames):
            self.movie = movie
            self.movieSelected = movieSelected
            self.directionMovieNames = directionMovieNames

            self.parentCell = None
            pass

        def getParentCell(self):
            return self.parentCell

        def setParentCell(self, cell):
            self.parentCell = cell
            pass

        def removeParentCell(self):
            self.parentCell = None
            pass

        def getMovie(self):
            return self.movie

        def getSelectedMovie(self):
            return self.movieSelected

        def getDirectionMovieNames(self):
            return self.directionMovieNames

    class ItemData(object):
        def __init__(self, id, row, column, name, movie, winMovie, crashMovie, directionMovie, winPos):
            self.id = id
            self.row = row
            self.column = column
            self.name = name
            self.movie = movie
            self.winMovie = winMovie
            self.crashMovie = crashMovie
            self.directionMovie = directionMovie
            self.winPos = winPos
            pass

        def getID(self):
            return self.id

        def getWinPos(self):
            return self.winPos

        def getRow(self):
            return self.row

        def getColumn(self):
            return self.column

        def getName(self):
            return self.name

        def getMovie(self):
            return self.movie

        def getWinMovie(self):
            return self.winMovie

        def getCrashMovie(self):
            return self.crashMovie

        def getDirectionMovie(self):
            return self.directionMovie
        pass

    @staticmethod
    def _onFinalize():
        PlumberManager.s_objects = {}
        pass

    @staticmethod
    def loadData(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("Name")
            fieldParam = values.get("Field")
            itemsParam = values.get("Items")
            cellItemsParam = values.get("CellItems")
            moviesParam = values.get("MovementMovies")
            buttonsParam = values.get("Buttons")
            metricX = values.get("MetricX")
            metricY = values.get("MetricY")

            cellWidth = values.get("CellWidth")
            cellHeight = values.get("CellHeight")
            wallsData = values.get("WallsData")

            Metric = (metricX, metricY)
            CellMetric = (cellWidth, cellHeight)

            object = EnigmaManager.getEnigmaObject(enigmaName)

            fieldData = PlumberManager.loadField(module, fieldParam)
            itemData = PlumberManager.loadItems(module, itemsParam, object)
            cellItemData = PlumberManager.loadCellItems(module, cellItemsParam, object)
            movementMovies = PlumberManager.loadMovementMovies(module, moviesParam, object)
            buttons = PlumberManager.loadButtons(module, buttonsParam, object)

            GameData = PlumberManager.Plumber(Metric, CellMetric, fieldData, itemData, cellItemData, movementMovies, wallsData, buttons)
            PlumberManager.s_objects[enigmaName] = GameData
            pass
        pass

    @staticmethod
    def loadButtons(module, collectionParam, enigmaObject):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        data = {}
        for values in records:
            name = values.get("Name")
            objectName = values.get("ObjectName")

            if enigmaObject.hasObject(objectName) is False:
                Trace.log("Manager", 0, "PlumberManager.loadMovementMovies", "object has no movieName: '%s' " % (objectName))
                # Trace.log("PlumberManager.loadMovementMovies", "object has no movieName: '%s' "%(objectName))
                pass
            object = enigmaObject.getObject(objectName)

            data[name] = object
            pass
        return data
        pass

    @staticmethod
    def loadMovementMovies(module, collectionParam, enigmaObject):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        data = {}
        for values in records:
            name = values.get("Name")
            movieName = values.get("MovieName")

            if enigmaObject.hasObject(movieName) is False:
                Trace.log("PlumberManager.loadMovementMovies", "object has no movieName: '%s' " % (movieName))
                pass

            movie = enigmaObject.getObject(movieName)

            data[name] = movie
            pass
        return data
        pass

    @staticmethod
    def loadCellItems(module, collectionParam, enigmaObject):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        data = {}
        for values in records:
            id = values.get("ID")
            movieName = values.get("MovieName")
            movieSelectedName = values.get("MovieSelectedName")
            directionMovieNames = values.get("DirectionMovieNames")

            if enigmaObject.hasObject(movieName) is False:
                Trace.log("PlumberManager.loadCellItems", "object has no movieName: '%s' " % (movieName))
                pass
            if enigmaObject.hasObject(movieSelectedName) is False:
                Trace.log("PlumberManager.loadCellItems", "object has no movieName: '%s' " % (movieSelectedName))
                pass

            movie = enigmaObject.getObject(movieName)
            movieSelected = enigmaObject.getObject(movieSelectedName)

            cellItem = PlumberManager.CellItem(movie, movieSelected, directionMovieNames)
            data[id] = cellItem
            pass
        return data
        pass

    @staticmethod
    def loadItems(module, collectionParam, enigmaObject):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        data = []
        for values in records:
            id = values.get("ID")
            row = values.get("Row")
            column = values.get("Column")
            name = values.get("Name")
            movieName = values.get("MovieName")
            winMovieName = values.get("WinMovieName")
            crashMovieName = values.get("CrashMovieName")
            directionMovieName = values.get("DirectionMovie")
            winPos = values.get("WinPos")

            if enigmaObject.hasObject(movieName) is False:
                Trace.log("PlumberManager.loadItems", "object has no movieName: '%s' " % (movieName))
                pass
            if enigmaObject.hasObject(winMovieName) is False:
                Trace.log("PlumberManager.loadItems", "object has no movieName: '%s' " % (winMovieName))
                pass
            if enigmaObject.hasObject(directionMovieName) is False:
                Trace.log("PlumberManager.loadItems", "object has no movieName: '%s' " % (directionMovieName))
                pass

            if enigmaObject.hasObject(crashMovieName) is False:
                Trace.log("PlumberManager.loadItems", "object has no movieName: '%s' " % (crashMovieName))
                pass

            movie = enigmaObject.getObject(movieName)
            winMovie = enigmaObject.getObject(winMovieName)
            crashMovie = enigmaObject.getObject(crashMovieName)
            directionMovie = enigmaObject.getObject(directionMovieName)

            itemData = PlumberManager.ItemData(id, row, column, name, movie, winMovie, crashMovie, directionMovie, winPos)
            data.append(itemData)
            pass
        return data
        pass

    @staticmethod
    def loadField(module, fieldParam):
        records = DatabaseManager.getDatabaseRecords(module, fieldParam)

        fieldData = {}
        for values in records:
            row = values.get("Row")
            values = values.get("Value")
            fieldData[row] = values
            pass
        return fieldData
        pass

    @staticmethod
    def getGameData(name):
        if PlumberManager.hasGameData(name) is False:
            return None
            pass
        record = PlumberManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasGameData(name):
        if name not in PlumberManager.s_objects:
            Trace.log("PlumberManager", 0, "PlumberManager.hasGameData: : invalid param")
            return False
            pass
        return True
