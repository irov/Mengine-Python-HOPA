from Foundation.DatabaseManager import DatabaseManager


class JoinBlocksManager(object):
    s_objects = {}

    class JoinBlocks(object):
        def __init__(self, blockName, blockPosition, blockStates, fieldHeight, fieldWidth, winLength):
            """  all args are list except first """
            self.blockName = blockName
            self.blockPosition = blockPosition
            self.blockStates = blockStates
            self.fieldHeight = fieldHeight
            self.fieldWidth = fieldWidth
            self.winLength = winLength

        def getBlockName(self):
            return self.blockName

        def getBlockPosition(self):
            return self.blockPosition

        def getBlockStates(self):
            return self.blockStates

        def getFieldHeight(self):
            return self.fieldHeight

        def getFieldWidth(self):
            return self.fieldWidth

        def getWinLength(self):
            return self.winLength

    @staticmethod
    def onFinalize():
        JoinBlocksManager.s_objects = {}
        pass

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        for values in records:
            enigmaName = values.get("Name")
            collectionParam = values.get("Collection")
            fieldHeight = values.get("FieldHeight")
            fieldWidth = values.get("FieldWidth")
            winLength = values.get("WinLength")
            JoinBlocksManager.loadJoinBlocksCollection(enigmaName, module, collectionParam, fieldHeight, fieldWidth, winLength)

        return True

    @staticmethod
    def loadJoinBlocksCollection(enigmaName, module, collectionParam, fieldHeight, fieldWidth, winLength):
        records = DatabaseManager.getDatabaseRecords(module, collectionParam)
        BlockList = []
        BlockPositionList = []
        BlockStateList = []

        for values in records:
            BlockName = values.get("BlockName")
            BlockList.append(BlockName)

            BlockPosition = values.get("BlockPosition")
            BlockPositionList.append(BlockPosition)

            States = values.get("States")
            BlockStateList.append(States)
            pass

        Object = JoinBlocksManager.JoinBlocks(BlockList, BlockPositionList, BlockStateList, fieldHeight, fieldWidth, winLength)
        JoinBlocksManager.s_objects[enigmaName] = Object
        pass

    @staticmethod
    def getJoinBlocks(name):
        if JoinBlocksManager.hasJoinBlocks(name) is False:
            return None
        record = JoinBlocksManager.s_objects[name]
        return record

    @staticmethod
    def hasJoinBlocks(name):
        if name not in JoinBlocksManager.s_objects:
            Trace.log("JoinBlocksManager", 0, "JoinBlocksManager.hasJoinBlocks: : invalid param")
            return False
        return True
