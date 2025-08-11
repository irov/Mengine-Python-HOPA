from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager


class EnigmaManager(Manager):
    s_enigmas = {}
    s_enigmaInventoryText = {}

    class Enigma(object):
        def __init__(self, ID, enigmaType, objectName, groupName, sceneName, movieWinObject, Skip, ZoomFrameGroup, Reset):
            self.id = ID
            self.objectName = objectName
            self.enigmaType = enigmaType
            self.groupName = groupName
            self.sceneName = sceneName
            self.movieWinObject = movieWinObject
            self.Skip = Skip
            self.ZoomFrameGroup = ZoomFrameGroup
            self.Reset = Reset

        def getGroupName(self):
            return self.groupName

        def getSceneName(self):
            return self.sceneName

        def getObjectName(self):
            return self.objectName

        def getObject(self):
            object = GroupManager.getObject(self.groupName, self.objectName)
            return object

        def getMovieWinObject(self):
            return self.movieWinObject

        def hasMovieWinObject(self):
            return self.movieWinObject is not None

        def getType(self):
            return self.enigmaType

        def getEntity(self):
            object = GroupManager.getObject(self.groupName, self.objectName)
            entity = object.getEntity()
            return entity

    @staticmethod
    def _onFinalize():
        EnigmaManager.s_enigmas = {}
        EnigmaManager.s_enigmaInventoryText = {}
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "Enigmas":
            return EnigmaManager.loadEnigmas(module, "Enigmas")
        if param == "PuzzleInventoryText":
            return EnigmaManager.loadEnigmaInventoryTexts(module, "PuzzleInventoryText")

        return False

    @staticmethod
    def loadEnigmas(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            ID = record.get("ID")
            Name = record.get("Name")
            Type = record.get("Type")
            ObjectName = record.get("ObjectName")
            GroupName = record.get("GroupName")
            SceneName = record.get("SceneName")
            MovieWinGroupName = record.get("MovieWinGroup")
            MovieName = record.get("MovieName")
            Skip = bool(record.get("Skip", False))
            ZoomFrameGroup = record.get("ZoomFrameGroup")
            Reset = bool(record.get("Reset", False))

            if EnigmaManager.addEnigma(ID, Name, Type, ObjectName, GroupName, SceneName, MovieWinGroupName, MovieName,
                                       Skip, ZoomFrameGroup, Reset) is False:
                return False

        return True

    @staticmethod
    def addEnigma(ID, Name, Type, ObjectName, GroupName, SceneName, MovieWinGroupName, MovieName, Skip, ZoomFrameGroup, Reset):
        MovieWinObject = None

        group = GroupManager.getGroup(GroupName)
        if isinstance(group, GroupManager.EmptyGroup):
            return True

        if MovieWinGroupName is not None:
            if MovieName is None:
                Trace.log("Manager", 0, "EnigmaManager.addEnigma: Enigma '%s' MovieName is None" % (Name))
                return False

            if GroupManager.hasObject(MovieWinGroupName, MovieName) is False:
                Trace.log("Manager", 0, "EnigmaManager.addEnigma: Enigma '%s' Movie '%s' is not found in Group '%s''" % (Name, MovieName, MovieWinGroupName))
                return False

            MovieWinObject = GroupManager.getObject(MovieWinGroupName, MovieName)

        if SceneManager.hasScene(SceneName) is False:
            Trace.log("Manager", 0, "EnigmaManager.addEnigma: Enigma '%s' not found scene '%s'" % (Name, SceneName))

        group = GroupManager.getGroup(GroupName)
        if isinstance(group, GroupManager.EmptyGroup):
            return True

        enigma = EnigmaManager.Enigma(ID, Type, ObjectName, GroupName, SceneName, MovieWinObject, Skip, ZoomFrameGroup, Reset)
        enigmaObject = GroupManager.getObject(GroupName, ObjectName)
        enigmaObject.setEnigmaName(Name)
        EnigmaManager.s_enigmas[Name] = enigma

        return True

    @staticmethod
    def loadEnigmaInventoryTexts(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("EnigmaName")
            TextID = record.get("TextID")

            EnigmaManager.s_enigmaInventoryText[Name] = TextID

        return True

    @staticmethod
    def getEnigmaName(object):
        if object is None:
            Trace.log("Manager", 0, "EnigmaManager: getEnigmaName, object is None")
            return None

        groupName = object.getGroupName()
        objectName = object.getName()

        for name, enigma in EnigmaManager.s_enigmas.items():
            enigmaGroupName = enigma.getGroupName()
            enigmaObjectName = enigma.getObjectName()
            if groupName == enigmaGroupName and objectName == enigmaObjectName:
                return name
        return None

    @staticmethod
    def getEnigmaInventoryText(name):
        if name not in EnigmaManager.s_enigmaInventoryText:
            return None

        return EnigmaManager.s_enigmaInventoryText[name]

    @staticmethod
    def hasEnigma(name):
        return name in EnigmaManager.s_enigmas

    @staticmethod
    def getEnigmaById(enigma_id):
        if enigma_id is None:
            Trace.log("Manager", 0, "EnigmaManager.getEnigmaById id is None")
            return None

        for enigma in EnigmaManager.s_enigmas.values():
            if enigma.id == enigma_id:
                return enigma

    @staticmethod
    def getEnigma(name):
        if name not in EnigmaManager.s_enigmas:
            Trace.log("Manager", 0, "EnigmaManager.getEnigma: not found Enigma %s" % (name))
            return None

        Enigma = EnigmaManager.s_enigmas[name]

        return Enigma

    @staticmethod
    def getEnigmaObject(name):
        if name not in EnigmaManager.s_enigmas:
            Trace.log("Manager", 0, "EnigmaManager.getEnigmaObject: not found Enigma %s" % (name))
            return None

        Enigma = EnigmaManager.getEnigma(name)
        groupName = Enigma.getGroupName()
        objectName = Enigma.getObjectName()
        object = GroupManager.getObject(groupName, objectName)

        return object

    @staticmethod
    def getEnigmaSceneName(name):
        if name not in EnigmaManager.s_enigmas:
            Trace.log("Manager", 0, "EnigmaManager.getEnigmaSceneName: not found Enigma %s" % (name))
            return None

        Enigma = EnigmaManager.getEnigma(name)
        sceneName = Enigma.getSceneName()

        return sceneName

    @staticmethod
    def getSceneEnigmas(sceneName):
        tempList = []
        for name, enigma in EnigmaManager.s_enigmas.items():
            if sceneName != enigma.sceneName:
                continue

            tempList.append(name)

        return tempList

    @staticmethod
    def getEnigmaGroupName(name):
        if name not in EnigmaManager.s_enigmas:
            Trace.log("Manager", 0, "EnigmaManager.getEnigmaGroupName: not found Enigma %s" % (name))
            return None

        Enigma = EnigmaManager.getEnigma(name)
        groupName = Enigma.getGroupName()

        return groupName

    @staticmethod
    def getSceneActiveEnigmaName(scene_name=None):
        enigma = EnigmaManager.getSceneActiveEnigma(scene_name)
        if enigma is None:
            return None
        name = enigma.getParam("EnigmaName")
        return name

    @staticmethod
    def getSceneActiveEnigma(scene_name=None):
        if scene_name is None:
            scene_name = SceneManager.getCurrentSceneName()

        if scene_name is None:
            return

        enigmas = EnigmaManager.getSceneEnigmas(scene_name)

        if enigmas is None:
            return

        for enigma_name in enigmas:
            enigma = EnigmaManager.getEnigmaObject(enigma_name)

            if not enigma.isActive():
                continue

            is_play = enigma.getParam("Play")
            is_pause = enigma.getParam("Pause")

            if is_play and not is_pause:
                return enigma
