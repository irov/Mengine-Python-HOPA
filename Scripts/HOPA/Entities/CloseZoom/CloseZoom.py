from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

class CloseZoom(BaseEntity):
    def _onActivate(self):
        self.onZoomEnterObserver = Notification.addObserver(Notificator.onZoomEnter, self._onZoomEnter)
        pass

    def _onDeactivate(self):
        Notification.removeObserver(self.onZoomEnterObserver)

        if TaskManager.existTaskChain("ClickButton_CloseZoom"):
            TaskManager.cancelTaskChain("ClickButton_CloseZoom")
            pass
        pass

    def _onZoomEnter(self, zoomGroupName):
        if self.object is None:
            return False

        if TaskManager.existTaskChain("ClickButton_CloseZoom"):
            TaskManager.cancelTaskChain("ClickButton_CloseZoom")
            pass

        ZoomCloseButtonPolicy = DefaultManager.getDefault("ZoomCloseButtonPolicy", "Auto")

        if ZoomCloseButtonPolicy == "Auto":
            buttonClose = self.object.getButtonClose()
            buttonCloseEntity = buttonClose.getEntity()
            buttonCloseSprite = buttonCloseEntity.getSprite()
            buttonCloseSpriteSize = buttonCloseSprite.getSurfaceSize()

            zoomGroupName = ZoomManager.getZoomOpenGroupName()
            zoomGroup = GroupManager.getGroup(zoomGroupName)

            ZoomPointRight = ZoomManager.calcZoomPointRight(zoomGroupName)

            if zoomGroup.hasObject("Point_CloseButton") is True:
                Position = zoomGroup.getObject("Point_CloseButton").getParam("Position")
            else:
                Position = (ZoomPointRight[0] - buttonCloseSpriteSize.x, ZoomPointRight[1])
                pass
            buttonCloseEntity.setLocalPosition(Position)
            pass

        elif ZoomCloseButtonPolicy == "Generate":
            pass

        with TaskManager.createTaskChain(Name="ClickButton_CloseZoom", Group=self.object, Repeat=True) as tc:
            tc.addTask("TaskButtonClick", ButtonName="Button_CloseZoom")
            tc.addTask("TaskFunction", Fn=self._closeZoom, Args=(zoomGroupName,))
            pass

        return False

    def _closeZoom(self, zoomGroupName):
        ZoomManager.closeZoom(zoomGroupName)

        return False
        pass

    pass