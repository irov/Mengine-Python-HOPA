from Foundation.Params import Params
from Foundation.SceneManager import SceneManager
from HOPA.ZoomManager import ZoomManager

class MixinZoomGroup(Params):
    def __init__(self):
        super(MixinZoomGroup, self).__init__()
        pass

    def _onParams(self, params):
        super(MixinZoomGroup, self)._onParams(params)

        self.SceneName = params.get("SceneName", None)
        self.ZoomGroupName = params.get("ZoomName", None)
        pass

    def _onInitialize(self):
        super(MixinZoomGroup, self)._onInitialize()

        if self.SceneName is None or self.ZoomGroupName is None:
            return
            pass

        if _DEVELOPMENT is True:
            if SceneManager.hasSceneZoom(self.SceneName, self.ZoomGroupName) is False:
                self.initializeFailed("invalid scene zoom %s:%s" % (self.SceneName, self.ZoomGroupName))
                pass
            pass
        pass

    def _onZoomFilter(self, ZoomGroupName):
        if self.ZoomGroupName != ZoomGroupName:
            return False
            pass

        return True
        pass

    def _onZoomAny(self, ZoomGroupName):
        return True
        pass

    def isZoomInit(self):
        return ZoomManager.isZoomInit(self.ZoomGroupName)
        pass

    def isZoomEnter(self):
        return ZoomManager.isZoomEnter(self.ZoomGroupName)
        pass

    def isZoomLeave(self):
        return ZoomManager.isZoomLeave(self.ZoomGroupName)
        pass
    pass