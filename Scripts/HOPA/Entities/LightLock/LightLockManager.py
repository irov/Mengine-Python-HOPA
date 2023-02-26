from Foundation.DatabaseManager import DatabaseManager

class LightLockManager(object):
    s_objects = {}

    class LightLockData(object):

        def __init__(self, socketData, stateData, winData, slotData, winMoviesData, waitData):
            self.socketData = socketData
            self.stateData = stateData
            self.winParam = winData
            self.slotData = slotData
            self.winMoviesData = winMoviesData
            self.waitData = waitData
            pass

        def getSocketData(self):
            return self.socketData
            pass

        def getStateData(self):
            return self.stateData
            pass

        def getWinParam(self):
            return self.winParam
            pass

        def getSlotData(self):
            return self.slotData
            pass

        def getWinMoviesData(self):
            return self.winMoviesData
            pass

        def getWaitData(self):
            return self.waitData
            pass

        pass

    @staticmethod
    def onFinalize():
        LightLockManager.s_objects = {}
        pass

    @staticmethod
    def loadLightLock(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("Name")
            SocketCollectionParam = values.get("SocketCollection")
            StateCollectionParam = values.get("StateCollection")
            WinParamCollection = values.get("WinParamCollection")
            SlotCollectionParam = values.get("SlotCollection")
            WinStateParam = values.get("WinStateCollection")
            WaitStateParam = values.get("WaitStateCollection")

            socketData = LightLockManager.loadSocketCollection(module, SocketCollectionParam)
            waitData = LightLockManager.loadWaitStateCollection(module, WaitStateParam)
            stateData = LightLockManager.loadStateCollection(module, StateCollectionParam)
            winData = LightLockManager.loadWinParam(module, WinParamCollection)
            slotData = LightLockManager.loadSlotCollection(module, SlotCollectionParam)
            winMoviesData = LightLockManager.loadWinStateCollection(module, WinStateParam)

            object = LightLockManager.LightLockData(socketData, stateData, winData, slotData, winMoviesData, waitData)

            LightLockManager.s_objects[enigmaName] = object
            pass
        pass

    @staticmethod
    def loadWaitStateCollection(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        waitData = {}

        for values in records:
            socketName = values.get("SocketName")
            value = values.get("Value")
            movieName = values.get("MovieName")

            if socketName not in waitData.keys():
                dict = {}
                dict[value] = movieName
                waitData[socketName] = dict
                pass
            else:
                internalDict = waitData[socketName]
                internalDict[value] = movieName
                waitData[socketName] = internalDict
                pass
            pass
        return waitData
        pass

    @staticmethod
    def loadSocketCollection(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        socketData = {}

        for values in records:
            socketName = values.get("SocketName")
            value = values.get("Value")
            movieName = values.get("MovieName")

            if socketName not in socketData.keys():
                dict = {}
                dict[value] = movieName
                socketData[socketName] = dict
                pass
            else:
                internalDict = socketData[socketName]
                internalDict[value] = movieName
                socketData[socketName] = internalDict
                pass
            pass
        return socketData
        pass

    @staticmethod
    def loadStateCollection(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        stateData = {}

        for value in records:
            socketName = value.get("SocketName")
            Value = value.get("Value")

            stateData[socketName] = Value
            pass

        return stateData
        pass

    @staticmethod
    def loadWinParam(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        winParam = []

        for value in records:
            Value1 = value.get("Value1")
            Value2 = value.get("Value2")

            winParam.append((Value1, Value2))
            pass

        return winParam
        pass

    @staticmethod
    def loadSlotCollection(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        slotData = {}

        for value in records:
            socketName = value.get("SocketName")
            slotName = value.get("SlotName")

            slotData[socketName] = slotName
            pass
        return slotData
        pass

    @staticmethod
    def loadWinStateCollection(module, collectionParam):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)

        winMoviesData = {}
        for value in records:
            SocketName = value.get("SocketName")
            RelatedSocket = value.get("RelatedSocket")
            WinMovieName = value.get("WinMovieName")

            winMoviesData[WinMovieName] = (SocketName, RelatedSocket)
            pass

        return winMoviesData
        pass

    @staticmethod
    def getLightLock(name):
        if LightLockManager.hasLightLock(name) is False:
            return None
            pass
        record = LightLockManager.s_objects[name]
        return record
        pass

    @staticmethod
    def hasLightLock(name):
        if name not in LightLockManager.s_objects:
            Trace.log("LightLockManager", 0, "LightLockManager.hasLightLock: : invalid param")
            return False
            pass
        return True
        pass

    pass

pass