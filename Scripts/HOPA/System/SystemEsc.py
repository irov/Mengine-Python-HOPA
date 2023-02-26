from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

class SystemEsc(System):
    def _onParams(self, params):
        super(SystemEsc, self)._onParams(params)
        self.layerFilter = {7: "Zoom", 6: "ItemPopUp", 5: "Journal", 4: "GUI", 3: "Options", 2: "Profile", 1: "Profile_New", 0: "Message"}
        pass

    def _onRun(self):
        self.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)
        pass

    def _onStop(self):
        return False
        pass

    def __onKeyEvent(self, key, x, y, isDown, isRepeating):
        if isDown != 1:
            return False
            pass

        if key != Mengine.KC_ESCAPE:
            return False
            pass

        CurrentSceneName = SceneManager.getCurrentSceneName()
        for id, layerName in self.layerFilter.items():
            if layerName == "Zoom":
                active = not ZoomManager.isZoomEmpty()
                pass
            else:
                if SceneManager.hasLayerScene(layerName) is False:
                    continue
                    pass
                LayerGroup = SceneManager.getSceneLayerGroup(CurrentSceneName, layerName)
                active = LayerGroup.getEnable()
                pass
            if active is False:
                continue
                pass
            else:
                Notification.notify(Notificator.onEscPressed, layerName)
                break
                pass
            pass
        else:
            # simple
            if SceneManager.hasLayerScene("GUI") is True:
                Notification.notify(Notificator.onEscPressed, "InGameOpen")
                pass
        return False
        pass