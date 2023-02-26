from Foundation.Initializer import Initializer
from HOPA.Prefetcher.PrefetchScope import PrefetchScope
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

DEBUG_MODE = True

# debug

# debug
def dumpPrefetch(prefetch):
    groups = prefetch.getGroupsList()
    for group in groups:
        print(group)
        pass
    pass

class Prefetcher(Initializer):
    def __init__(self):
        super(Prefetcher, self).__init__()
        self.currentPrefetchScope = PrefetchScope()
        self.loadedPrefetch = self.currentPrefetchScope
        # debug
        self.groupsTrace = {}
        pass

    def _onInitialize(self):
        super(Prefetcher, self)._onInitialize()
        self.onSceneInitObserver = Notification.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        self.onZoomBlockOpen = Notification.addObserver(Notificator.onZoomBlockOpen, self.__onZoomBlockOpen)
        self.onTransitionBlockOpenObserver = Notification.addObserver(Notificator.onTransitionBlockOpen, self.__onTransitionBlockOpen)
        self.onSceneLeaveObserver = Notification.addObserver(Notificator.onSceneLeave, self.__onSceneLeave)
        # self.onObjectEnableObserver = Notification.addObserver("onObjectEnable", self.__onObjectEnable)

        # for debug
        if DEBUG_MODE is False:
            return
            pass

        self.onKeyEventObserver = Notification.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)
        pass

    def _onFinalize(self):
        super(Prefetcher, self)._onFinalize()
        Notification.removeObserver(self.onSceneInitObserver)
        Notification.removeObserver(self.onTransitionBlockOpenObserver)
        Notification.removeObserver(self.onZoomBlockOpen)
        Notification.removeObserver(self.onSceneLeaveObserver)
        # Notification.removeObserver( self.onObjectEnableObserver )

        # for debug
        if DEBUG_MODE is False:
            return
            pass

        Notification.removeObserver(self.onKeyEventObserver)
        pass

    #########################################################

    def __onSceneInit(self, sceneName):
        # print "Prefetch __onSceneInit", sceneName
        newPrefetchScope = PrefetchScope()
        oldPrefetchScope = self.currentPrefetchScope

        # debug
        if DEBUG_MODE is True:
            self.__addToHistory(oldPrefetchScope)
            pass

        if self._isCompletePrefetch(oldPrefetchScope) is False:
            # print "<<<<<<<<<<<<<<<<<<INTERRUPT"
            self._forceLoadPrefetch(oldPrefetchScope)
            pass

        newPrefetchScope.onInitialize(sceneName)

        # loadedPrefetch = self._getPrefetchDifference(newPrefetchScope,oldPrefetchScope)
        # unloadedPrefetch = self._getPrefetchDifference(oldPrefetchScope,newPrefetchScope)
        # self.loadedPrefetch = loadedPrefetch
        # self._loadPrefetch( loadedPrefetch )
        # self._decreasePrefetch( unloadedPrefetch )
        # print "LOAD!!!"
        # dumpPrefetch(loadedPrefetch)

        intersectPrefetch = self._getPrefetchIntersect(newPrefetchScope, oldPrefetchScope)
        self._loadPrefetch(intersectPrefetch)
        self._loadPrefetch(newPrefetchScope)
        self._unloadPrefetch(oldPrefetchScope)
        self._unloadPrefetch(intersectPrefetch)

        self.currentPrefetchScope = newPrefetchScope
        return False
        pass

    def _getPrefetchIntersect(self, prefetchScope1, prefetchScope2):
        intersectPrefetch = prefetchScope1.getIntersection(prefetchScope2)
        return intersectPrefetch
        pass

    def _getPrefetchDifference(self, prefetchScope1, prefetchScope2):
        diffPrefetch = prefetchScope1.getDifference(prefetchScope2)
        return diffPrefetch
        pass

    def __onSceneLeave(self, sceneName):
        return False
        pass

    #    def __onObjectEnable(self,object):
    #        type = object.getType()
    #        if type == "ObjectZoom":
    #            blockOpen = object.getParam("BlockOpen")
    #            state = self.__onZoomBlockOpen(object,blockOpen)
    #            return state
    #            pass
    #        elif type == "ObjectTransition":
    #            blockOpen = object.getParam("BlockOpen")
    #            state = self.__onTransitionBlockOpen(object,blockOpen)
    #            return state
    #            pass
    #        else:
    #            return False
    #            pass
    #        pass

    def __onZoomBlockOpen(self, object, value):
        if value is True:
            return False
            pass

        group = object.getGroup()
        sceneName = group.getSceneName()

        if self.currentPrefetchScope.getSceneName() != sceneName:
            return False
            pass

        enable = object.getParam("Enable")
        if enable is False:
            return False
            pass

        ZoomGroupName = ZoomManager.getZoomGroupName(object)

        self.currentPrefetchScope.addZoom(ZoomGroupName)
        self._loadPrefetch(self.currentPrefetchScope)
        # debug
        return False
        pass

    def __onTransitionBlockOpen(self, object, value):
        if value is True:
            return False
            pass

        group = object.getGroup()
        sceneName = group.getSceneName()

        if self.currentPrefetchScope.getSceneName() != sceneName:
            return False
            pass

        enable = object.getParam("Enable")
        if enable is False:
            return False
            pass

        sceneTo = TransitionManager.getTransitionSceneTo(object)
        if self.currentPrefetchScope.isNeighbor(sceneTo):
            return
            pass

        self.currentPrefetchScope.addGroupsFromScene(sceneTo)
        self._loadPrefetch(self.currentPrefetchScope)

        return False
        pass

    def __onKeyEvent(self, key, x, y, isDown, isRepeating):
        if isDown != 1:
            return False
            pass

        if key == Mengine.KC_S:
            for group in self.groupsTrace.itervalues():
                print(group)
                pass
        elif key == Mengine.KC_D:
            dumpPrefetch(self.currentPrefetchScope)
            pass

        return False
        pass

    ##################################################################

    # debug
    def __addToHistory(self, prefetchScope):
        if DEBUG_MODE is False:
            return
            pass

        groups = prefetchScope.getGroupsList()
        for group in groups:
            groupName = group.getName()
            self.groupsTrace[groupName] = group
            pass
        pass

    def _loadPrefetch(self, prefetchScope):
        prefetchScope.load()
        pass

    def _unloadPrefetch(self, prefetchScope):
        prefetchScope.unload()
        pass

    def _forceLoadPrefetch(self, prefetchScope):
        prefetchScope.forceLoad()
        pass

    def _decreasePrefetch(self, prefetchScope):
        prefetchScope.decrease()
        pass

    def _isCompletePrefetch(self, prefetchScope):
        state = prefetchScope.isComplete()
        return state
        pass