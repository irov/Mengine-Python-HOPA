from Foundation.Initializer import Initializer
from Foundation.SceneManager import SceneManager
from HOPA.Prefetcher.GroupPrefetch import GroupPrefetch
from HOPA.Prefetcher.GroupPrefetchManager import GroupPrefetchManager
from HOPA.Prefetcher.PrefetchLoader import PrefetchLoader
from HOPA.TransitionManager import TransitionManager
from HOPA.ZoomManager import ZoomManager

class PrefetchScope(Initializer):
    def __init__(self):
        self.__groups = {}
        self.__loader = PrefetchLoader()
        self.__neighbors = []
        self.__sceneName = None
        pass

    def _onInitialize(self, sceneName):
        super(PrefetchScope, self)._onInitialize(sceneName)
        self.__sceneName = sceneName
        self.addZoomsFromScene(sceneName)
        self.__collectNeighbors(sceneName)
        pass

    def getSceneName(self):
        return self.__sceneName
        pass

    def isNeighbor(self, sceneName):
        if sceneName in self.__neighbors:
            return True
            pass
        return False
        pass

    def __collectNeighbors(self, sceneName):
        transitions = TransitionManager.getOpenSceneTransitions(sceneName)
        if transitions is None:
            return
            pass

        for transition in transitions:
            sceneTo = TransitionManager.getTransitionSceneTo(transition)
            self.addGroupsFromScene(sceneTo)
            pass
        pass

    def addZoomsFromScene(self, sceneName):
        zooms = ZoomManager.getActiveSceneZooms(sceneName)
        if zooms is None:
            return
            pass

        for zoom in zooms:
            groupName = ZoomManager.getZoomGroupName(zoom)
            self.addZoom(groupName)
            pass
        pass

    def addZoom(self, groupName):
        self.addGroup(groupName, GroupPrefetch.PRIORITY_ZOOM)
        pass

    def isZoom(self, groupName):
        return ZoomManager.hasZoom(groupName)
        pass

    def addGroupsFromScene(self, sceneName):
        if SceneManager.hasScene(sceneName) is False:
            Trace.log("Manager", 0, "_addSceneGroupsToPrefetch sceneName %s not exist" % sceneName)
            return None
            pass

        if sceneName in self.__neighbors:
            Trace.log("Manager", 0, "_addGroupsFromScene sceneName %s already exist in prefetch" % sceneName)
            return None
            pass

        self.__neighbors.append(sceneName)
        sceneGroups = SceneManager.getSceneGroups(sceneName)
        for groupName in sceneGroups:
            if self.isZoom(groupName) is True:
                continue
                pass

            self.addGroup(groupName, GroupPrefetch.PRIORITY_COMMON)
            pass
        pass

    def getIntersection(self, prefech):
        intersectPrefetch = PrefetchScope()

        def __addIntersectGroup(group):
            name = group.getName()
            if self.hasGroup(name) is False:
                return
                pass
            intersectPrefetch.addGroupPrefetch(group)
            pass

        prefech.visitGroups(__addIntersectGroup)
        return intersectPrefetch
        pass

    def getDifference(self, prefech):
        differencePrefetch = PrefetchScope()

        groups = self.getGroupsList()
        for group in groups:
            name = group.getName()
            if prefech.hasGroup(name) is True:
                continue
                pass
            differencePrefetch.addGroupPrefetch(group)

        return differencePrefetch
        pass

    def visitGroups(self, visitor):
        groupsList = self.getGroupsList()
        for group in groupsList:
            visitor(group)
            pass
        pass

    def addGroups(self, groups):
        for groupPrefetch in groups:
            self.addGroupPrefetch(groupPrefetch)
            pass
        pass

    def addGroup(self, groupName, priority):
        if self.hasGroup(groupName) is True:
            Trace.log("Manager", 0, "group %s already exist in prefetch" % groupName)
            return
            pass

        groupPrefetch = GroupPrefetchManager.getGroupPrefetch(groupName)
        if groupPrefetch is None:
            return
            pass

        if groupPrefetch.isEmpty() is True:
            return
            pass

        groupPrefetch.setPriority(priority)
        self.addGroupPrefetch(groupPrefetch)
        pass

    def addGroupPrefetch(self, groupPrefetch):
        groupName = groupPrefetch.getName()
        self.__groups[groupName] = groupPrefetch
        self.__loader.addGroupPrefetch(groupPrefetch)
        pass

    def hasGroup(self, groupName):
        if groupName not in self.__groups:
            return False
            pass
        return True
        pass

    def getGroup(self, groupName):
        if self.hasGroup(groupName) is False:
            return None
            pass
        group = self.__groups[groupName]
        return group
        pass

    ###############################################################################

    def load(self):
        if self.__loader.isLoading() is True:
            return
            pass
        self.__loader.start()
        pass

    def decrease(self):
        if self.__loader.isLoading() is True:
            return
            pass
        self.__loader.unloadAll()
        pass

    def forceLoad(self):
        self.__loader.forceLoading()
        pass

    def unload(self):
        self.__loader.unloadLoaded()
        pass

    def isComplete(self):
        state = self.__loader.isComplete()
        return state
        pass

    def getGroupsList(self):
        groupsList = [group for name, group in self.__groups.items()]
        return groupsList
        pass