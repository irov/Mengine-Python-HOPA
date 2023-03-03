from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.TransitionManager import TransitionManager


class SystemTransitionPrefetcher(System):
    def __init__(self):
        super(SystemTransitionPrefetcher, self).__init__()

        self.prefetchGroups = []
        pass

    def _onRun(self):
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.addObserver(Notificator.onTransitionBegin, self.__onTransitionBegin)
        self.addObserver(Notificator.onTransitionBlockOpen, self.__onTransitionBlockOpen)
        self.addObserver(Notificator.onTransitionEnable, self.__onTransitionEnable)
        return True
        pass

    def _onStop(self):
        self.__unfetchGroups([])
        pass

    def __onTransitionEnable(self, object, value):
        self.__onTransitionBlockOpen(object, not value)

        return False
        pass

    def __onTransitionBlockOpen(self, object, value):
        SceneTo = TransitionManager.getTransitionSceneTo(object)

        if SceneTo is None:
            return False
            pass

        GroupName = SceneManager.getSceneMainGroupName(SceneTo)

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

        # if self.prefetchSceneToGroup is not None:
        #     Mengine.unfetchResources(self.prefetchSceneToGroup)
        #     self.prefetchSceneToGroup = None
        #     pass

        sceneActiveTransitions = TransitionManager.getActiveSceneTransitions(SceneName)

        for transition in sceneActiveTransitions:
            GroupName = SceneManager.getSceneMainGroupName(transition.sceneNameTo)

            self.__prefetchGroup(GroupName)
            pass

        SceneBack = TransitionManager.getTransitionBack(SceneName)

        if SceneBack is not None:
            GroupName = SceneManager.getSceneMainGroupName(SceneBack)

            self.__prefetchGroup(GroupName)
            pass

        return False
        pass

    def __onTransitionBegin(self, SceneFrom, SceneTo, ZoomGroupName):
        if SceneManager.isGameScene(SceneFrom) is False:
            return False
            pass

        if SceneManager.isGameScene(SceneTo) is False:
            return False
            pass

        exception = []

        prefetchSceneFromGroup = SceneManager.getSceneMainGroupName(SceneFrom)
        prefetchSceneToGroup = SceneManager.getSceneMainGroupName(SceneTo)

        exception.append(prefetchSceneFromGroup)
        exception.append(prefetchSceneToGroup)

        self.__unfetchGroups(exception)

        return False
        pass

    def __unfetchGroups(self, exception):
        for groupName in self.prefetchGroups[:]:
            if groupName in exception:
                continue
                pass

            Mengine.unfetchResources(groupName)

            self.prefetchGroups.remove(groupName)
            pass
        pass

    def __prefetchGroup(self, groupName):
        if groupName in self.prefetchGroups:
            return
            pass

        def __cb(successful, GroupName):
            # print "SystemTransitionPrefetcher Prefetch", successful, GroupName
            pass

        Mengine.prefetchResources(groupName, __cb, groupName)

        self.prefetchGroups.append(groupName)
        pass

    def __unfetchGroup(self, groupName):
        if groupName not in self.prefetchGroups:
            return
            pass

        self.prefetchGroups.remove(groupName)

        Mengine.unfetchResources(groupName)
        pass

    pass
