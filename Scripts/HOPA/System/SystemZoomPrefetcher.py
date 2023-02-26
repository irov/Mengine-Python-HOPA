from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.ZoomManager import ZoomManager

class SystemZoomPrefetcher(System):
    def __init__(self):
        super(SystemZoomPrefetcher, self).__init__()

        self.onSceneInitObserver = None
        self.onZoomBlockOpenObserver = None
        self.onZoomEnableObserver = None

        self.prefetchGroups = []
        pass

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.addObserver(Notificator.onTransitionBegin, self.__onTransitionBegin)
        self.addObserver(Notificator.onZoomBlockOpen, self.__onZoomBlockOpen)
        self.addObserver(Notificator.onZoomEnable, self.__onZoomEnable)

        return True
        pass

    def _onStop(self):
        self.__unfetchGroups()
        pass

    def __onZoomEnable(self, object, value):
        self.__onZoomBlockOpen(object, not value)

        return False
        pass

    def __onZoomBlockOpen(self, object, value):
        GroupName = ZoomManager.getZoomGroupName(object)

        if value is True:
            self.__unfetchGroup(GroupName)
            pass
        else:
            self.__prefetchGroup(GroupName)
            pass

        return False
        pass

    def __onSceneInit(self, SceneName):
        if SceneManager.isGameScene(SceneName) is False:
            return False
            pass

        sceneActiveZooms = ZoomManager.getActiveSceneZooms(SceneName)

        for zoom in sceneActiveZooms:
            GroupName = zoom.getGroupName()

            self.__prefetchGroup(GroupName)
            pass

        return False
        pass

    def __onTransitionBegin(self, SceneFrom, SceneTo, ZoomGroupName):
        self.__unfetchGroups()

        return False
        pass

    def __unfetchGroups(self):
        for groupName in self.prefetchGroups:
            Mengine.unfetchResources(groupName)
            pass

        self.prefetchGroups = []
        pass

    def __prefetchGroup(self, groupName):
        if groupName in self.prefetchGroups:
            return
            pass

        self.prefetchGroups.append(groupName)

        def __cb(successful, GroupName):
            # print "SystemZoomPrefetcher Prefetch", successful, GroupName
            pass

        Mengine.prefetchResources(groupName, __cb, groupName)
        pass

    def __unfetchGroup(self, groupName):
        if groupName not in self.prefetchGroups:
            return
            pass

        self.prefetchGroups.remove(groupName)

        Mengine.unfetchResources(groupName)
        pass
    pass