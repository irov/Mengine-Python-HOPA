from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from HOPA.WalktrhoughTextManager import WalktrhoughTextManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification


class WalktrhoughText(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "Open")
        pass

    def __init__(self):
        super(WalktrhoughText, self).__init__()
        pass

    def _onActivate(self):
        #        self.isEnable = False
        self.currentSceneName = None

        self.Text_Message = self.object.getObject("Text_Message")
        self.Background = self.object.getObject("Sprite_Background")

        if self.Open is False:
            self.Text_Message.setEnable(False)
            self.Background.setEnable(False)
            #            return
            pass
        else:
            self.Text_Message.setEnable(True)
            self.Background.setEnable(True)
            pass

        self.onKeyEventObserver = Notification.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)
        self.onZoomEnterObserver = Notification.addObserver(Notificator.onZoomEnter, self._onZoomEnter)
        self.onZoomLeaveObserver = Notification.addObserver(Notificator.onZoomLeave, self._onZoomLeave)
        self.onSceneEnterObserver = Notification.addObserver(Notificator.onSceneEnter, self._onSceneEnter)
        pass

    def _onDeactivate(self):
        self.Text_Message = None
        self.Background = None

        Notification.removeObserver(self.onKeyEventObserver)
        Notification.removeObserver(self.onZoomEnterObserver)
        Notification.removeObserver(self.onZoomLeaveObserver)
        Notification.removeObserver(self.onSceneEnterObserver)
        pass

    def _onSceneEnter(self, sceneName):
        self.currentSceneName = SceneManager.getCurrentSceneName()
        self.__updateText()
        return False
        pass

    def _onZoomLeave(self, zoomGroupName):
        self.currentSceneName = SceneManager.getCurrentSceneName()
        self.__updateText()
        return False
        pass

    def _onZoomEnter(self, zoomGroupName):
        self.currentSceneName = ZoomManager.getZoomOpenGroupName()
        self.__updateText()
        return False
        pass

    def __updateText(self):
        textID = WalktrhoughTextManager.getTextID(self.currentSceneName)
        self.Text_Message.setTextID(textID)
        pass

    def __onKeyEvent(self, key, x, y, isDown, isRepeating):
        #        if ZoomManager.getZoomOpenGroupName() is not None:
        #            self.currentSceneName = ZoomManager.getZoomOpenGroupName()
        #            pass
        #        else:
        #            self.currentSceneName = SceneManager.getCurrentSceneName()
        #            pass
        #
        #        textID = WalktrhoughTextManager.getTextID(self.currentSceneName)
        #        self.Text_Message.setTextID(textID)

        if isDown != 1:
            return False
            pass

        if key == Mengine.KC_H:
            if self.Open is False:
                self.object.setOpen(True)
                self.Text_Message.setEnable(True)
                self.Background.setEnable(True)
                return False
                pass
            pass

        self.Text_Message.setEnable(False)
        self.Background.setEnable(False)
        #        self.isEnable = False
        self.object.setOpen(False)

        return False
        pass
