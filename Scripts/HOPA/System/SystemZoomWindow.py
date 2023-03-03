from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.System import System
from HOPA.ZoomManager import ZoomManager


class SystemZoomWindow(System):
    def _onParams(self, params):
        super(SystemZoomWindow, self)._onParams(params)
        self.frameGroups = params.get("FrameGroups", None)
        pass

    def _onRun(self):
        self.Window = None
        self.addObserver(Notificator.onZoomInit, self._onZoomInit)
        self.addObserver(Notificator.onZoomLeave, self._onZoomLeave)

        return True
        pass

    def _onStop(self):
        self.__cleanData()
        pass

    def _onZoomInit(self, zoomGroupName):
        zoom = ZoomManager.getZoom(zoomGroupName)
        zoomFrameGroupName = zoom.getFrameGroupName()

        if self.frameGroups is not None:
            if zoomFrameGroupName not in self.frameGroups:
                return False
                pass
            pass

        Window = DemonManager.getDemon("ZoomWindow")
        WindowGroup = Window.getGroup()
        zoomGroup = GroupManager.getGroup(zoomGroupName)
        zoomScene = zoomGroup.getScene()
        mainLayer = zoomGroup.getMainLayer()

        sizeZoom = mainLayer.getSize()
        Window.setClientSize(sizeZoom)

        zoomPoint = ZoomManager.getZoomPoint(zoom, zoomGroup)
        Window.setPosition(zoomPoint)

        # if GroupManager.hasObject(zoomFrameGroupName, "Demon_ZoomFrame"):
        #     Demon_ZoomFrame = GroupManager.getObject(zoomFrameGroupName, "Demon_ZoomFrame")
        #     # Demon_ZoomFrame.setPosition(zoomPoint)
        #     pass
        #
        # if GroupManager.hasObject(zoomFrameGroupName, "Demon_CloseZoom"):
        #     Demon_CloseZoom = GroupManager.getObject(zoomFrameGroupName, "Demon_CloseZoom")
        #     # Demon_CloseZoom.setPosition(zoomPoint)
        #     pass

        # windowEntity = self.Window.getEntity()
        # zoomScene.addChild(windowEntity)

        posZoom = ZoomManager.calcZoomPointLeft(zoomGroupName)

        ZoomButtonOffsetX = DefaultManager.getDefaultFloat("ZoomButtonOffsetX", 0)
        ZoomButtonOffsetY = DefaultManager.getDefaultFloat("ZoomButtonOffsetY", 0)

        finalPos = (posZoom[0] + sizeZoom.x - ZoomButtonOffsetX, posZoom[1] - ZoomButtonOffsetY)

        CloseZoom = None
        if WindowGroup.hasObject("Demon_CloseZoom"):
            CloseZoom = WindowGroup.getObject("Demon_CloseZoom")
            pass
        elif DemonManager.hasDemon("CloseZoom"):
            CloseZoom = DemonManager.getDemon("CloseZoom")
            pass

        if CloseZoom is None:
            return False
            pass

        ButtonClose = CloseZoom.getButtonClose()
        ButtonClose.setPosition(finalPos)

        return False
        pass

    def _onZoomLeave(self, zoomGroupName):
        self.__cleanData()

        return False
        pass

    def __cleanData(self):
        # if self.Window is None:
        #     return

        # windowEntity = self.Window.getEntity()
        # windowEntity.removeFromParent()
        # self.Window = None
        pass

    pass
