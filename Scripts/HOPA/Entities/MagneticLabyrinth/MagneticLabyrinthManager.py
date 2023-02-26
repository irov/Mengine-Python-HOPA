from Foundation.DatabaseManager import DatabaseManager

class MagneticLabyrinthManager(object):
    s_objects = {}

    class MagneticLabyrinth(object):
        def __init__(self, metric, speed, data):
            self.metric = metric
            self.speed = speed
            self.data = data
            pass

        def getMetric(self):
            return self.metric
            pass

        def getData(self):
            return self.data
            pass

        def getSpeed(self):
            return self.speed
            pass

        pass

    @staticmethod
    def onFinalize():
        MagneticLabyrinthManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("Name")
            collectionParam = values.get("Collection")
            metricX = values.get("MetricX")
            metricy = values.get("MetricY")
            speed = values.get("Speed")
            speed *= 0.001  # speed fix
            Metric = (metricX, metricy)
            MagneticLabyrinthManager.loadCollection(enigmaName, module, collectionParam, Metric, speed)
            pass
        pass

    @staticmethod
    def loadCollection(enigmaName, module, collectionParam, metric, speed):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        fieldData = {}
        for values in records:
            row = values.get("Row")
            values = values.get("Value")
            fieldData[row] = values
            pass
        GameData = MagneticLabyrinthManager.MagneticLabyrinth(metric, speed, fieldData)
        MagneticLabyrinthManager.s_objects[enigmaName] = GameData
        pass

    @staticmethod
    def getGameData(name):
        if MagneticLabyrinthManager.hasGameData(name) is False:
            return None
            pass
        record = MagneticLabyrinthManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasGameData(name):
        if name not in MagneticLabyrinthManager.s_objects:
            Trace.log("MagneticLabyrinthManager", 0, "MagneticLabyrinthManager.hasGameData: : invalid param")
            return False
            pass
        return True
        pass
    pass