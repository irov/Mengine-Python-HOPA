from Foundation.ArrowManager import ArrowManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.ZoomManager import ZoomManager
from Notification import Notification

class Zoom(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "Polygon", Update=Zoom._restorePolygon)
        Type.addAction(Type, "HintPoint")
        Type.addAction(Type, "Point")
        Type.addAction(Type, "BlockOpen")
        Type.addAction(Type, "End")
        pass

    def __init__(self):
        super(Zoom, self).__init__()

        self.hotspot = None
        pass

    def _restorePolygon(self, value):
        self.hotspot.setPolygon(value)
        pass

    def __updateBlockOpen(self, value):
        Notification.notify(Notificator.onTransitionBlockOpen, self.object, value)
        pass

    def _onInitialize(self, obj):
        super(Zoom, self)._onInitialize(obj)

        self.hotspot = self.createChild("HotSpotPolygon")

        self.hotspot.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent, onHandleMouseEnter=self._onMouseEnter, onHandleMouseLeave=self._onMouseLeave, onHandleMouseButtonEventBegin=self._onMouseButtonEventBegin, onHandleMouseButtonEventEnd=self._onMouseButtonEventEnd)
        self.hotspot.disable()
        pass

    def _onUpdateEnable(self, value):
        Notification.notify(Notificator.onZoomEnable, self.object, value)
        pass

    def _onFinalize(self):
        super(Zoom, self)._onFinalize()

        Mengine.destroyNode(self.hotspot)
        self.hotspot = None
        pass

    def getHotSpot(self):
        return self.hotspot
        pass

    def _updateInteractive(self, value):
        if value is True:
            self.hotspot.enable()
        else:
            self.hotspot.disable()
            pass
        pass

    def _onMouseEnter(self, x, y):
        if self.BlockOpen is True:
            return False
            pass

        zoomGroupName = ZoomManager.getZoomGroupName(self.object)

        Zoom = ZoomManager.getZoom(zoomGroupName)

        if Zoom is None:
            Trace.log("Object", 0, "Zoom._onMouseEnter: %s:%s not found zoom %s [maybe add to Zooms.xlsx]" % (self.object.getGroupName(), self.getName(), zoomGroupName))
            return False
            pass

        ZoomSceneName = Zoom.getFromSceneName()
        currentSceneName = SceneManager.getCurrentSceneName()

        if ZoomSceneName != currentSceneName:
            return False
            pass

        Notification.notify(Notificator.onZoomMouseEnter, self.object)

        return True
        pass

    def _onMouseLeave(self):
        if self.BlockOpen is True:
            return
            pass

        zoomGroupName = ZoomManager.getZoomGroupName(self.object)

        Zoom = ZoomManager.getZoom(zoomGroupName)

        ZoomSceneName = Zoom.getFromSceneName()
        currentSceneName = SceneManager.getCurrentSceneName()

        if ZoomSceneName != currentSceneName:
            return
            pass

        Notification.notify(Notificator.onZoomMouseLeave, self.object)
        pass

    def _onMouseButtonEvent(self, touchId, x, y, button, pressure, isDown, isPressed):
        zoomGroupName = ZoomManager.getZoomGroupName(self.object)

        Zoom = ZoomManager.getZoom(zoomGroupName)

        ZoomSceneName = Zoom.getFromSceneName()
        currentSceneName = SceneManager.getCurrentSceneName()

        if ZoomSceneName != currentSceneName:
            return False
            pass

        def _DefaultImplementation():
            if button == 0 and isDown == 1:
                if ArrowManager.emptyArrowAttach() is False:
                    Notification.notify(Notificator.onZoomUse, self.object)

                Notification.notify(Notificator.onZoomClick, self.object)

        def _TouchpadImplementation():
            if TaskManager.existTaskChain("ZoomMouseButtonEventTC") is True:
                return
            with TaskManager.createTaskChain(Name="ZoomMouseButtonEventTC") as tc:
                tc.addDelay(100.0)  # wait, may be user scroll
                if button == 0 and isDown == 1:
                    if ArrowManager.emptyArrowAttach() is False:
                        tc.addNotify(Notificator.onZoomUse, self.object)
                    tc.addNotify(Notificator.onZoomClick, self.object)

        if Mengine.hasTouchpad() is True:
            _TouchpadImplementation()
        else:
            _DefaultImplementation()

        return True
        pass

    def _onMouseButtonEventEnd(self, touchId, x, y, button, pressure, isDown, isPressed):
        if button == 0 and isDown == 1:
            Notification.notify(Notificator.onZoomClickEnd, self.object)
            pass

        return False
        pass

    def _onMouseButtonEventBegin(self, touchId, x, y, button, pressure, isDown, isPressed):
        if button == 0 and isDown == 1:
            Notification.notify(Notificator.onZoomClickBegin, self.object)
            pass

        return False
        pass

    def isMouseEnter(self):
        hotspot = self.getHotSpot()

        pickerOver = hotspot.isMousePickerOver()

        return pickerOver
        pass

    pass