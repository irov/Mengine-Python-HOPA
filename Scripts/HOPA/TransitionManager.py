from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from Graph import Graph
from HOPA.EnigmaManager import EnigmaManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class TransitionManager(object):
    s_transition = []
    s_transitionBack = {}
    s_transitionBackShow = {}
    s_inMovies = {}
    s_outMovies = {}
    s_openZooms = {}

    s_transitionBackObject = None
    s_transitionBackCursor = "TransitionBack"

    s_block = 0

    onTransitionMouseEnterObserver = None
    onTransitionClickObserver = None
    onTransitionMouseLeaveObserver = None

    class TransitionDesc(object):
        def __init__(self, object, sceneNameFrom, sceneNameTo, cursorMode, sceneNameShow):
            self.object = object
            self.sceneNameFrom = sceneNameFrom
            self.sceneNameTo = sceneNameTo
            self.cursorMode = cursorMode
            self.sceneNameShow = sceneNameShow
            pass

        pass

    @staticmethod
    def onInitialize():
        TransitionManager.onTransitionMouseEnterObserver = Notification.addObserver(Notificator.onTransitionMouseEnter, TransitionManager.__transitionMouseEnter)
        TransitionManager.onTransitionClickObserver = Notification.addObserver(Notificator.onTransitionClick, TransitionManager.__transitionClick)
        TransitionManager.onTransitionMouseLeaveObserver = Notification.addObserver(Notificator.onTransitionMouseLeave, TransitionManager.__transitionMouseLeave)
        pass

    @staticmethod
    def onFinalize():
        TransitionManager.s_transition = []

        Notification.removeObserver(TransitionManager.onTransitionMouseEnterObserver)
        Notification.removeObserver(TransitionManager.onTransitionClickObserver)
        Notification.removeObserver(TransitionManager.onTransitionMouseLeaveObserver)
        pass

    @staticmethod
    def hasInMovie(groupName, transitionName):
        if (groupName, transitionName) not in TransitionManager.s_inMovies:
            return False
            pass

        return True
        pass

    @staticmethod
    def hasOutMovie(groupName, transitionName):
        if (groupName, transitionName) not in TransitionManager.s_outMovies:
            return False
            pass

        return True
        pass

    @staticmethod
    def getInMovie(groupName, transitionName):
        MovieObject = TransitionManager.s_inMovies[(groupName, transitionName)]

        return MovieObject
        pass

    @staticmethod
    def getOutMovie(groupName, transitionName):
        MovieObject = TransitionManager.s_outMovies[(groupName, transitionName)]

        return MovieObject
        pass

    @staticmethod
    def getInMovies():
        return TransitionManager.s_inMovies.values()
        pass

    @staticmethod
    def getOutMovies():
        return TransitionManager.s_outMovies.values()
        pass

    @staticmethod
    def hasTransitionBack(sceneNameFrom):
        if sceneNameFrom not in TransitionManager.s_transitionBack:
            return False
            pass

        return True
        pass

    @staticmethod
    def getTransitionBack(sceneNameFrom):
        if sceneNameFrom not in TransitionManager.s_transitionBack:
            return None
            pass

        sceneNameTo = TransitionManager.s_transitionBack[sceneNameFrom]

        return sceneNameTo
        pass

    @staticmethod
    def setTransitionBack(sceneNameFrom, sceneNameTo):
        TransitionManager.s_transitionBack[sceneNameFrom] = sceneNameTo

    @staticmethod
    def popTransitionBack(sceneNameFrom):
        if sceneNameFrom in TransitionManager.s_transitionBack:
            return TransitionManager.s_transitionBack.pop(sceneNameFrom)

    @staticmethod
    def getTransitionBackShow(sceneNameFrom):
        if sceneNameFrom not in TransitionManager.s_transitionBackShow:
            return None
            pass

        sceneNameTo = TransitionManager.s_transitionBackShow[sceneNameFrom]

        return sceneNameTo
        pass

    @staticmethod
    def popTransitionBackShow(sceneNameFrom):
        if sceneNameFrom in TransitionManager.s_transitionBackShow:
            return TransitionManager.s_transitionBackShow.pop(sceneNameFrom)

    @staticmethod
    def setTransitionBackShow(sceneNameFrom, sceneNameTo):
        TransitionManager.s_transitionBackShow[sceneNameFrom] = sceneNameTo

    @staticmethod
    def getTransitionBackObject():
        return TransitionManager.s_transitionBackObject
        pass

    @staticmethod
    def _setupTransitionBackObject():
        if Mengine.hasTouchpad():
            demon_name = "Navigation"
            object_name = "Movie2Button_NavGoBack"
        else:
            demon_name = "TransitionBack"
            object_name = "Transition_Back"

        if DemonManager.hasDemon(demon_name) is False:
            Trace.log("Manager", 0, "TransitionManager.loadTransitionBack: invalid demon {}".format(demon_name))
            return

        Demon_TransitionBack = DemonManager.getDemon(demon_name)
        TransitionManager.s_transitionBackObject = Demon_TransitionBack.getObject(object_name)

    @staticmethod
    def loadTransitionBack(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        TransitionManager._setupTransitionBackObject()

        for record in records:
            SceneFrom = record.get("SceneFrom")
            SceneTo = record.get("SceneTo")
            SceneToShow = record.get("Text_ID")

            OpenZoomName = record.get("OpenZoomName")

            TransitionManager.s_openZooms[(SceneFrom, SceneTo)] = OpenZoomName

            TransitionManager.s_transitionBack[SceneFrom] = SceneTo
            TransitionManager.s_transitionBackShow[SceneFrom] = SceneToShow
            pass
        pass

    @staticmethod
    def loadParams(module, param):
        if param == "Transition":
            TransitionManager.loadTransition(module, "Transition")
            pass
        if param == "TransitionBack":
            TransitionManager.loadTransitionBack(module, "TransitionBack")
            pass

        return True
        pass

    @staticmethod
    def loadTransition(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            GroupName = record.get("GroupName")
            TransitionName = record.get("TransitionName")
            SceneNameFrom = record.get("SceneNameFrom")
            SceneNameTo = record.get("SceneNameTo")
            CursorMode = record.get("CursorMode")
            OpenZoomName = record.get("OpenZoomName")
            SceneNameShow = record.get("SceneNameID", None)

            TransitionManager.s_openZooms[(SceneNameFrom, SceneNameTo)] = OpenZoomName

            TransitionManager.setTransition(GroupName, TransitionName, SceneNameFrom, SceneNameTo, CursorMode, SceneNameShow)
            pass
        pass

    @staticmethod
    def loadTransitionMovies(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            GroupName = record.get("GroupName")
            TransitionName = record.get("TransitionName")

            MovieInGroupName = record.get("MovieFadeInGroup", None)
            MovieInName = record.get("MovieFadeInName", None)

            if MovieInName is not None:
                if MovieInGroupName is None:
                    MovieInGroupName = GroupName

                if GroupManager.hasObject(MovieInGroupName, MovieInName) is False:
                    Trace.log("Manager", 0, "TransitionManager.loadTransitionMovies: Group '%s' not found movie '%s'" % (MovieInGroupName, MovieInName,))
                    return False

                MovieObject = GroupManager.getObject(MovieInGroupName, MovieInName)
                TransitionManager.s_inMovies[(GroupName, TransitionName)] = MovieObject

            MovieOutGroupName = record.get("MovieFadeOutGroup", None)
            MovieOutName = record.get("MovieFadeOutName", None)
            if MovieOutName is not None:
                if MovieOutGroupName is None:
                    MovieOutGroupName = GroupName

                if GroupManager.hasObject(MovieOutGroupName, MovieOutName) is False:
                    Trace.log("Manager", 0, "TransitionManager.loadTransitionMovies: Group '%s' not found movie '%s'" % (MovieOutGroupName, MovieOutName,))
                    return False

                MovieObject = GroupManager.getObject(MovieOutGroupName, MovieOutName)
                TransitionManager.s_outMovies[(GroupName, TransitionName)] = MovieObject

    @staticmethod
    def setTransition(groupName, objectName, sceneNameFrom, sceneNameTo, cursorMode, SceneNameShow):
        if SceneManager.hasScene(sceneNameFrom) is False and ZoomManager.hasZoom(sceneNameFrom) is False:
            Trace.log("Transition", 0, "Transition.setTransition: not find fromSceneName %s" % (sceneNameFrom))
            return
            pass

        if SceneManager.hasScene(sceneNameTo) is False:
            Trace.log("Transition", 0, "Transition.setTransition: not find toSceneName %s" % (sceneNameTo))
            return
            pass

        group = GroupManager.getGroup(groupName)
        if isinstance(group, GroupManager.EmptyGroup):
            return

        if group is None:
            Trace.log("Transition", 0, "Transition.setTransition: group %s not found" % (groupName))
            return
            pass

        if group.hasObject(objectName) is False:
            Trace.log("Transition", 0, "Transition.setTransition: not found object %s:%s" % (groupName, objectName))
            return
            pass

        transitionObject = group.getObject(objectName)

        transition = TransitionManager.TransitionDesc(transitionObject, sceneNameFrom, sceneNameTo, cursorMode, SceneNameShow)

        TransitionManager.s_transition.append(transition)
        pass

    @staticmethod
    def blockTransition(value, isGameScene):
        if value is True:
            TransitionManager.s_block += 1
        else:
            TransitionManager.s_block -= 1
            pass

        block = TransitionManager.s_block != 0

        Notification.notify(Notificator.onTransitionBlock, block, isGameScene)
        pass

    @staticmethod
    def _changeScene(transition):
        SceneNameTo = TransitionManager.getTransitionSceneTo(transition)

        if SceneNameTo is None:
            return
            pass

        CurrentSceneName = SceneManager.getCurrentSceneName()

        openZoomName = TransitionManager.getOpenZoomName(CurrentSceneName, SceneNameTo)

        MovieInObject = None
        transitionGroupName = transition.getGroupName()
        transitionName = transition.getName()
        if TransitionManager.hasInMovie(transitionGroupName, transitionName) is True:
            MovieInObject = TransitionManager.getInMovie(transitionGroupName, transitionName)
            pass

        MovieOutObject = None
        transitionGroupName = transition.getGroupName()
        transitionName = transition.getName()
        if TransitionManager.hasOutMovie(transitionGroupName, transitionName) is True:
            MovieOutObject = TransitionManager.getOutMovie(transitionGroupName, transitionName)
            pass

        if MovieOutObject is None:
            DefaultFadeOutGroup = DefaultManager.getDefault("TransitionFadeOutGroup", None)
            TransitionFadeOutMovie = DefaultManager.getDefault("TransitionFadeOutMovie", None)
            if DefaultFadeOutGroup is not None and TransitionFadeOutMovie is not None:
                MovieOutObject = GroupManager.getObject(DefaultFadeOutGroup, TransitionFadeOutMovie)
                pass
            pass

        TransitionBackObject = TransitionManager.getTransitionBackObject()

        if TransitionBackObject is transition:
            scene_to = TransitionManager.getTransitionSceneTo(transition)
            transition_to = TransitionManager.findTransitionObjectToScene(scene_to, CurrentSceneName)

            TaskManager.runAlias("AliasTransition", None, SceneName=SceneNameTo, ZoomGroupName=openZoomName,
                                 MovieIn=MovieInObject, MovieOut=MovieInObject,
                                 ZoomEffectTransitionBackObject=transition_to)
        else:
            TaskManager.runAlias("AliasTransition", None, SceneName=SceneNameTo, ZoomGroupName=openZoomName,
                                 MovieIn=MovieInObject, MovieOut=MovieOutObject, ZoomEffectTransitionObject=transition)

    @staticmethod
    def changeScene(sceneName, zoomGroupName=None, fade=True, Cb=None):
        if sceneName is None:
            Trace.log("Manager", 0, "TransitionManager.changeScene sceneName is None!!!!!")
        TaskManager.runAlias("AliasTransition", Cb, SceneName=sceneName, ZoomGroupName=zoomGroupName, Fade=fade)

    @staticmethod
    def changeToGameScene(fade=True):
        gameSceneName = SceneManager.getCurrentGameSceneName()
        gameZoomName = ZoomManager.getCurrentGameZoomName()

        TransitionManager.changeScene(gameSceneName, gameZoomName, fade=fade)
        pass

    @staticmethod
    def isValidTransition(transitionObject, SceneName):
        # if TransitionManager.isBlockTransition() is True:
        #     return False
        #     pass

        for transition in TransitionManager.s_transition:
            if transition.object is not transitionObject:
                continue
                pass

            if transition.sceneNameFrom == SceneName:
                return True
                pass
            pass

        if TransitionManager.hasTransitionBack(SceneName) is True:
            return True
            pass

        return False
        pass

    @staticmethod
    def getTransitionSceneTo(transitionObject):
        for transition in TransitionManager.s_transition:
            if transition.object is not transitionObject:
                continue
                pass

            return transition.sceneNameTo
            pass

        TransitionBackObject = TransitionManager.getTransitionBackObject()

        if TransitionBackObject is transitionObject:
            CurrentSceneName = SceneManager.getCurrentSceneName()

            if TransitionManager.hasTransitionBack(CurrentSceneName) is True:
                sceneNameTo = TransitionManager.getTransitionBack(CurrentSceneName)

                return sceneNameTo
                pass
            pass

        return None
        pass

    @staticmethod
    def getTransitionSceneNameTo(transitionObject):
        for transition in TransitionManager.s_transition:
            if transition.object is not transitionObject:
                continue
                pass

            return transition.sceneNameShow
            pass

        TransitionBackObject = TransitionManager.getTransitionBackObject()

        if TransitionBackObject is transitionObject:
            CurrentSceneName = SceneManager.getCurrentSceneName()

            if TransitionManager.hasTransitionBack(CurrentSceneName) is True:
                sceneNameTo = TransitionManager.getTransitionBackShow(CurrentSceneName)

                return sceneNameTo
                pass
            pass

        return None
        pass

    @staticmethod
    def getTransitionCursor(transitionObject, SceneName):
        for transition in TransitionManager.s_transition:
            if transition.object is not transitionObject:
                continue
                pass

            if transition.sceneNameFrom == SceneName:
                return transition.cursorMode
                pass
            pass

        TransitionBackObject = TransitionManager.getTransitionBackObject()

        if TransitionBackObject is transitionObject:
            return TransitionManager.s_transitionBackCursor
            pass

        return None
        pass

    @staticmethod
    def getOpenZoomName(sceneNameFrom, sceneNameTo):
        key = (sceneNameFrom, sceneNameTo)
        if key not in TransitionManager.s_openZooms.keys():
            return None
            pass

        return TransitionManager.s_openZooms[key]
        pass

    @staticmethod
    def isBlockTransition():
        if TransitionManager.s_block != 0:
            return True
            pass

        return False
        pass

    @staticmethod
    def __transitionClick(transition):
        BlockOpen = transition.getParam("BlockOpen")
        if BlockOpen is True:
            return False
            pass

        BlockGameScenes = SceneManager.isBlockGameScenes()
        if BlockGameScenes is True:
            return False
            pass
        SceneName = SceneManager.getCurrentSceneName()
        Enigmas = EnigmaManager.getSceneEnigmas(SceneName)
        if Enigmas is not None:
            for name in Enigmas:
                obj = EnigmaManager.getEnigmaObject(name)

                if not obj.isActive():
                    continue

                play = obj.getParam("Play")
                EnigmaPause = obj.getParam("Pause")

                if (play is True) and (EnigmaPause is False):
                    with TaskManager.createTaskChain(Name="TransitionClick_CONFIRM", Repeat=False) as tc:
                        tc.addTask("AliasMessageShow", TextID="ID_POPUP_CONFIRM_MiniGame_QUIT")

                        with tc.addRaceTask(2) as (tc_no, tc_yes):
                            tc_no.addTask("AliasMessageNo")
                            with tc_no.addParallelTask(2) as (tc_no_1, tc_no_2):
                                tc_no_1.addTask("AliasMessageHide")

                            tc_yes.addTask("AliasMessageYes")
                            with tc_yes.addParallelTask(2) as (tc_yes_1, tc_yes_2):
                                tc_yes_1.addTask("AliasMessageHide")
                                tc_yes_1.addFunction(TransitionManager.transitionClick_end, transition)
                    return False

        TransitionManager.transitionClick_end(transition)
        return False

    @staticmethod
    def transitionClick_end(transition):
        ZoomOpenGroupName = ZoomManager.getZoomOpenGroupName()
        if ZoomOpenGroupName is not None:
            ZoomManager.closeZoom(ZoomOpenGroupName)
            pass

        Notification.notify(Notificator.onSoundEffectOnObject, transition, "TransitionClick")
        Notification.notify(Notificator.onTransitionChangeScene, transition)

        TransitionManager._changeScene(transition)

        return False

    @staticmethod
    def __transitionMouseEnter(transition):
        return False
        pass

    @staticmethod
    def __transitionMouseLeave(transition):
        return False
        pass

    @staticmethod
    def getTransition(sceneNameFrom, sceneNameTo):
        for transition in TransitionManager.s_transition:
            if transition.sceneNameFrom != sceneNameFrom:
                continue
                pass

            if transition.sceneNameTo != sceneNameTo:
                continue
                pass

            return transition.object
            pass

        return None
        pass

    @staticmethod
    def getOpenSceneTransitions(sceneName):
        listTransitions = []
        for transition in TransitionManager.s_transition:
            if transition.sceneNameFrom != sceneName:
                continue
                pass

            if transition.object.getEnable() is False:
                continue
                pass

            if transition.object.getBlockOpen() is True:
                continue
                pass

            if transition.object.getBlockInteractive() is True:
                continue
                pass

            listTransitions.append(transition.object)
            pass

        return listTransitions
        pass

    @staticmethod
    def getActiveSceneTransitions(sceneName):
        listTransitions = []
        for transition in TransitionManager.s_transition:
            if transition.sceneNameFrom != sceneName:
                continue
                pass

            if transition.object.getEnable() is False:
                continue
                pass

            if transition.object.getBlockOpen() is True:
                continue
                pass

            if transition.object.getBlockInteractive() is True:
                continue
                pass

            listTransitions.append(transition)
            pass

        return listTransitions
        pass

    @staticmethod
    def getActiveSceneTransitionObjects(sceneName):
        transitionObjects = []

        for transition in TransitionManager.s_transition:
            if transition.sceneNameFrom != sceneName:
                continue

            if transition.object.getEnable() is False:
                continue

            if transition.object.getBlockOpen() is True:
                continue

            if transition.object.getBlockInteractive() is True:
                continue

            transitionObjects.append(transition.object)

        return transitionObjects

    @staticmethod
    def findSpiralScenes(sceneName):
        transitionGraph = TransitionManager.__makeTransitionGraph()
        sceneNode = transitionGraph.findNode(sceneName)

        nodeSpiral = transitionGraph.findSpiral(sceneNode)

        transitionGraph.destroy()

        if nodeSpiral is None:
            return []
            pass

        scenes = [node.value for node in nodeSpiral]

        return scenes
        pass

    @staticmethod
    def __makeTransitionGraph():
        transitionGraph = Graph()

        sceneNodes = {}

        for transition in TransitionManager.s_transition:
            if transition.object.getEnable() is False:
                continue
                pass

            if transition.sceneNameFrom not in sceneNodes:
                node = transitionGraph.createNode(transition.sceneNameFrom)
                sceneNodes[transition.sceneNameFrom] = node
                pass

            if transition.sceneNameTo not in sceneNodes:
                node = transitionGraph.createNode(transition.sceneNameTo)
                sceneNodes[transition.sceneNameTo] = node
                pass

            sceneNodeFrom = sceneNodes[transition.sceneNameFrom]
            sceneNodeTo = sceneNodes[transition.sceneNameTo]

            sceneNodeFrom.addLink(sceneNodeTo)
            pass

        for sceneNameFrom, sceneNameTo in TransitionManager.s_transitionBack.iteritems():
            if sceneNameFrom not in sceneNodes:
                node = transitionGraph.createNode(sceneNameFrom)
                sceneNodes[sceneNameFrom] = node
                pass

            if sceneNameTo not in sceneNodes:
                node = transitionGraph.createNode(sceneNameTo)
                sceneNodes[sceneNameTo] = node
                pass

            sceneNodeFrom = sceneNodes[sceneNameFrom]
            sceneNodeTo = sceneNodes[sceneNameTo]

            sceneNodeFrom.addLink(sceneNodeTo)
            pass

        return transitionGraph
        pass

    @staticmethod
    def findTransitionObjectToScene(sceneNameFrom, sceneNameTo):
        if sceneNameFrom == sceneNameTo:
            Trace.log("Manager", 0, "TransitionManager.findTransitionObjectToScene: sceneNameFrom (%s) equal sceneNameTo (%s)" % (sceneNameFrom, sceneNameTo))
            return None
            pass

        transitionGraph = TransitionManager.__makeTransitionGraph()

        sceneNodeFrom = transitionGraph.findNode(sceneNameFrom)
        sceneNodeTo = transitionGraph.findNode(sceneNameTo)

        way = transitionGraph.findWay(sceneNodeFrom, sceneNodeTo)

        if len(way) == 1:
            sceneNodeFirstStep = sceneNodeTo
        else:
            sceneNodeFirstStep = way[1]
            pass

        TransitionBackObject = TransitionManager.getTransitionBackObject()

        if len(way) > 2:
            indexSceneNext = 0
            for sceneNodeStep in way[:-1]:
                sceneNameCurrent = sceneNodeStep.value
                indexSceneNext += 1
                sceneNodeStepNext = way[indexSceneNext]
                sceneNameNext = sceneNodeStepNext.value

                tempTransitionObject = TransitionManager.getTransition(sceneNameCurrent, sceneNameNext)
                if tempTransitionObject is not None:
                    if tempTransitionObject.getEnable() is False or tempTransitionObject.isInteractive() is False:
                        transitionGraph.destroy()
                        return None
                        pass

                    sceneGroupName = SceneManager.getSceneMainGroupName(sceneNameCurrent)
                    transitionGroupName = tempTransitionObject.getGroupName()
                    if transitionGroupName != sceneGroupName:
                        isZoom = ZoomManager.hasZoom(transitionGroupName)
                        if isZoom is False:
                            return None
                            pass
                        ZoomObject = ZoomManager.getZoomObject(transitionGroupName)
                        if ZoomObject.getEnable() is False or ZoomObject.isInteractive() is False:
                            return None
                            pass
                        pass
                    pass

                elif TransitionManager.hasTransitionBack(sceneNameCurrent) is True:
                    TransitionBackScene = TransitionManager.getTransitionBack(sceneNameCurrent)
                    if sceneNameNext != TransitionBackScene:
                        transitionGraph.destroy()
                        return None
                        pass
                    if TransitionBackObject.getEnable() is False or TransitionBackObject.isInteractive() is False:
                        transitionGraph.destroy()
                        return None
                        pass
                    pass
                elif tempTransitionObject is None:
                    return None
                    pass
                pass
            pass

        transitionGraph.destroy()

        if sceneNodeFirstStep is None:
            return None

        sceneNameFirstStep = sceneNodeFirstStep.value

        TransitionObject = TransitionManager.getTransition(sceneNameFrom, sceneNameFirstStep)

        if TransitionObject is not None:
            sceneGroupName = SceneManager.getSceneMainGroupName(sceneNameFrom)
            transitionGroupName = TransitionObject.getGroupName()
            if transitionGroupName == sceneGroupName:
                # if TransitionObject.isActive() is False or TransitionObject.getEnable() is False:
                if TransitionObject.getEnable() is False or TransitionObject.isInteractive() is False:
                    return None
                    pass
                return TransitionObject
                pass

            isZoom = ZoomManager.hasZoom(transitionGroupName)
            if isZoom is False:
                return None
                pass
            ZoomObject = ZoomManager.getZoomObject(transitionGroupName)
            if ZoomObject.getEnable() is False:
                return None
                pass

            return TransitionObject
            pass

        if TransitionManager.hasTransitionBack(sceneNameFrom) is True:
            TransitionBackScene = TransitionManager.getTransitionBack(sceneNameFrom)
            if TransitionBackScene == sceneNameFirstStep:
                return TransitionBackObject
                pass
            pass

        return None
        pass

    @staticmethod
    def findTransitionBackToScene(sceneNameFrom, sceneNameTo):
        if sceneNameFrom == sceneNameTo:
            Trace.log("Manager", 0, "TransitionManager.findTransitionObjectToScene: sceneNameFrom (%s) equal sceneNameTo (%s)" % (sceneNameFrom, sceneNameTo))
            return None
            pass

        transitionGraph = TransitionManager.__makeTransitionGraph()

        sceneNodeFrom = transitionGraph.findNode(sceneNameFrom)
        sceneNodeTo = transitionGraph.findNode(sceneNameTo)

        way = transitionGraph.findWay(sceneNodeFrom, sceneNodeTo)

        transitionGraph.destroy()

        if len(way) == 1:
            sceneNodeFirstStep = sceneNodeTo
        else:
            sceneNodeFirstStep = way[1]
            pass

        sceneNameFirstStep = sceneNodeFirstStep.value

        if TransitionManager.hasTransitionBack(sceneNameFrom) is False:
            return None
            pass

        SceneNameTo = TransitionManager.getTransitionBack(sceneNameFrom)

        if SceneNameTo != sceneNameFirstStep:
            return None
            pass

        TransitionBack = TransitionManager.getTransitionBackObject()

        return TransitionBack
