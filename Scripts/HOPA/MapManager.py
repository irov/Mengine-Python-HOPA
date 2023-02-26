from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager

class MapManager(object):
    s_teleports = {}
    s_chapterGroups = {}
    s_macroTypeFilter = []

    class Teleport(object):
        def __init__(self, sceneName, clickObject):
            self.sceneName = sceneName
            self.clickObject = clickObject
            pass

        def getClickObject(self):
            return self.clickObject
            pass
        pass

    @staticmethod
    def onFinalize():
        MapManager.s_objects = {}
        pass

    @staticmethod
    def loadMacroTypeFilter(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            CommandName = record.get("CommandName")

            MapManager.s_macroTypeFilter.append(CommandName)
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "MapChapters":
            MapManager.loadChapterGroups(module, "MapChapters")
            pass
        if param == "MapMacroTypeFilter":
            MapManager.loadMacroTypeFilter(module, "MapMacroTypeFilter")
            pass
        pass

    @staticmethod
    def loadChapterGroups(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Chapter = record.get("Chapter")
            GroupName = record.get("GroupName")
            Param = record.get("Param")

            MapManager.loadMapTeleports(Chapter, GroupName, Param)
            MapManager.s_chapterGroups[Chapter] = GroupName
            pass
        pass

    @staticmethod
    def getMacroTypeFilter():
        if len(MapManager.s_macroTypeFilter) == 0:
            Trace.log("Manager", 0, "MapManager.getMacroTypeFilter: MacroTypeFilter is empty")
            return None
            pass

        return MapManager.s_macroTypeFilter
        pass

    @staticmethod
    def addChapterPage(id):
        DemonMap = DemonManager.getDemon("Map")
        groupName = MapManager.s_chapterGroups[id]
        DemonMap.setCurrentID(groupName)
        OpenPages = DemonMap.getOpenPages()
        newIndex = len(OpenPages)
        newIndex += 1
        DemonMap.changeParam("OpenPages", newIndex, groupName)
        pass

    @staticmethod
    def loadMapTeleports(Chapter, GroupName, module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ObjectName = record.get("ObjectName")
            SceneNameTo = record.get("SceneNameTo")

            MapManager.addMapTeleport(Chapter, GroupName, ObjectName, SceneNameTo)
            pass
        pass

    @staticmethod
    def addMapTeleport(Chapter, GroupName, teleportName, sceneName):
        if teleportName in MapManager.s_teleports:
            Trace.log("Manager", 0, "MapManager addMapTransition: object %s already exist" % (teleportName))
            return
            pass

        clickObject = GroupManager.getObject(GroupName, teleportName)
        Teleport = MapManager.Teleport(sceneName, clickObject)
        MapManager.s_teleports.setdefault(GroupName, []).append(Teleport)
        pass

    @staticmethod
    def getTeleportSceneName(teleportName):
        if teleportName not in MapManager.s_teleports:
            return None
            pass

        return MapManager.s_teleports[teleportName].sceneName
        pass

    @staticmethod
    def getChapterTeleports(name):
        return MapManager.s_teleports[name]
        pass
    pass