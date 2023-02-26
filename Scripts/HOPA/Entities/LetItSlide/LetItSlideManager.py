from Foundation.DatabaseManager import DatabaseManager
from HOPA.EnigmaManager import EnigmaManager

class LetItSlideManager(object):
    s_objects = {}

    class LetItSlide(object):
        def __init__(self, metric, cellMetric, fieldData, itemData, winCombination):
            self.metric = metric
            self.cellMetric = cellMetric
            self.fieldData = fieldData
            self.itemData = itemData
            self.winCombination = winCombination
            pass

        def getWinCombination(self):
            return self.winCombination
            pass

        def getMetric(self):
            return self.metric
            pass

        def getCellMetric(self):
            return self.cellMetric
            pass

        def getFieldData(self):
            return self.fieldData
            pass

        def getItemData(self):
            return self.itemData
            pass
        pass

    class LetItSlideItem(object):
        def __init__(self, position, movieObject, length, isHorizontal):
            self.position = position
            self.movieObject = movieObject
            self.isHorizontal = isHorizontal
            self.length = length
            pass

        def getPosition(self):
            return self.position
            pass

        def getMovieObject(self):
            return self.movieObject
            pass

        def getHorizontal(self):
            return self.isHorizontal
            pass

        def getLength(self):
            return self.length
            pass
        pass

    @staticmethod
    def onFinalize():
        LetItSlideManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("Name")
            fieldParam = values.get("FieldParam")
            itemsParam = values.get("ItemsParam")
            winParam = values.get("WinParam")

            metricX = values.get("MetricX")
            metricY = values.get("MetricY")

            cellWidth = values.get("CellWidth")
            cellHeight = values.get("CellHeight")

            Metric = (metricX, metricY)
            CellMetric = (cellWidth, cellHeight)

            object = EnigmaManager.getEnigmaObject(enigmaName)

            fieldData = LetItSlideManager.loadField(module, fieldParam)
            itemData = LetItSlideManager.loadItems(module, itemsParam, object)
            currentWinComb = LetItSlideManager.loadWinCombination(module, winParam)

            GameData = LetItSlideManager.LetItSlide(Metric, CellMetric, fieldData, itemData, currentWinComb)

            LetItSlideManager.s_objects[enigmaName] = GameData
            pass
        pass

    @staticmethod
    def loadItems(module, itemsParam, object):
        records = DatabaseManager.getDatabaseRecords(module, itemsParam)

        itemData = {}
        for record in records:
            id = record.get("ID")
            row = record.get("Row")
            column = record.get("Column")
            movieName = record.get("MovieName")
            length = record.get("Length")
            isHorizontal = bool(record.get("isHorizontal"))

            position = (row, column)
            movieObject = object.getObject(movieName)

            item = LetItSlideManager.LetItSlideItem(position, movieObject, length, isHorizontal)
            itemData[id] = item
            pass
        return itemData
        pass

    @staticmethod
    def loadWinCombination(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        win = {}
        for record in records:
            itemID = record.get("ItemID")
            row = record.get("Row")
            column = record.get("Column")

            winPosition = (row, column)

            win[itemID] = winPosition
            pass
        return win
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
        if LetItSlideManager.hasGameData(name) is False:
            return None
            pass
        record = LetItSlideManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasGameData(name):
        if name not in LetItSlideManager.s_objects:
            Trace.log("PlumberManager", 0, "PlumberManager.hasGameData: : invalid param")
            return False
            pass
        return True
        pass
    pass
    pass