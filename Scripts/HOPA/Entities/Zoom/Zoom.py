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

        self.hotspot.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent,
                                      onHandleMouseEnter=self._onMouseEnter,
                                      onHandleMouseLeave=self._onMouseLeave,
                                      onHandleMouseButtonEventBegin=self._onMouseButtonEventBegin,
                                      onHandleMouseButtonEventEnd=self._onMouseButtonEventEnd)
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

    def _onMouseEnter(self, context, event):
        if self.BlockOpen is True:
            return False
            pass

        zoomGroupName = ZoomManager.getZoomGroupName(self.object)

        Zoom = ZoomManager.getZoom(zoomGroupName)

        if Zoom is None:
            Trace.log("Object", 0, "Zoom._onMouseEnter: %s:%s not found zoom %s [maybe add to Zooms.xlsx]" % (self.object.getGroupName(), self.getName(), zoomGroupName))
            return False

        ZoomSceneName = Zoom.getFromSceneName()
        currentSceneName = SceneManager.getCurrentSceneName()

        if ZoomSceneName != currentSceneName:
            return False

        Notification.notify(Notificator.onZoomMouseEnter, self.object)

        return True

    def _onMouseLeave(self, context, event):
        if self.BlockOpen is True:
            return

        zoomGroupName = ZoomManager.getZoomGroupName(self.object)

        Zoom = ZoomManager.getZoom(zoomGroupName)

        ZoomSceneName = Zoom.getFromSceneName()
        currentSceneName = SceneManager.getCurrentSceneName()

        if ZoomSceneName != currentSceneName:
            return

        Notification.notify(Notificator.onZoomMouseLeave, self.object)
        pass

    def _onMouseButtonEvent(self, context, event):
        zoomGroupName = ZoomManager.getZoomGroupName(self.object)

        Zoom = ZoomManager.getZoom(zoomGroupName)

        ZoomSceneName = Zoom.getFromSceneName()
        currentSceneName = SceneManager.getCurrentSceneName()

        if ZoomSceneName != currentSceneName:
            return False

        def _DefaultImplementation():
            if event.button == Mengine.MC_LBUTTON and event.isDown == 1:
                if ArrowManager.emptyArrowAttach() is False:
                    Notification.notify(Notificator.onZoomUse, self.object)

                Notification.notify(Notificator.onZoomClick, self.object)

        def _TouchpadImplementation():
            if TaskManager.existTaskChain("ZoomMouseButtonEventTC") is True:
                return
            with TaskManager.createTaskChain(Name="ZoomMouseButtonEventTC") as tc:
                tc.addDelay(100.0)  # wait, may be user scroll
                if event.button == Mengine.MC_LBUTTON and event.isDown == 1:
                    if ArrowManager.emptyArrowAttach() is False:
                        tc.addNotify(Notificator.onZoomUse, self.object)
                    tc.addNotify(Notificator.onZoomClick, self.object)

        if Mengine.hasTouchpad() is True:
            _TouchpadImplementation()
        else:
            _DefaultImplementation()

        return True

    def _onMouseButtonEventEnd(self, context, event):
        if event.button == Mengine.MC_LBUTTON and event.isDown == 1:
            Notification.notify(Notificator.onZoomClickEnd, self.object)
            pass

        return False

    def _onMouseButtonEventBegin(self, context, event):
        if event.button == Mengine.MC_LBUTTON and event.isDown == 1:
            Notification.notify(Notificator.onZoomClickBegin, self.object)
            pass

        return False

    def isMouseEnter(self):
        hotspot = self.getHotSpot()

        pickerOver = hotspot.isMousePickerOver()

        return pickerOver
    pass
