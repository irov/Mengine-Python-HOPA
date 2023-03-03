from Foundation.ArrowManager import ArrowManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.SceneManager import SceneManager
from HOPA.TransitionManager import TransitionManager
from Notification import Notification


class Transition(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "Polygon", Update=Transition._restorePolygon)
        Type.addAction(Type, "HintPoint")
        Type.addActionActivate(Type, "BlockOpen", Update=Transition.__updateBlockOpen)
        pass

    NotificatorTransitionEnterDict = {
        "TransitionHOG": Notificator.onTransitionHOGMouseEnter,
        "TransitionUp": Notificator.onTransitionUpMouseEnter,
        "TransitionBack": Notificator.onTransitionBackMouseEnter,
        "TransitionLeft": Notificator.onTransitionLeftMouseEnter,
        "TransitionRight": Notificator.onTransitionRightMouseEnter,
        "TransitionPuzzle": Notificator.onTransitionPuzzleMouseEnter,
        "TransitionUpLeft": Notificator.onTransitionUpLeftMouseEnter,
        "TransitionUpRight": Notificator.onTransitionUpRightMouseEnter,
        "Transition": Notificator.onTransitionMouseEnter
    }

    NotificatorTransitionLeaveDict = {
        "TransitionHOG": Notificator.onTransitionHOGMouseLeave,
        "TransitionUp": Notificator.onTransitionUpMouseLeave,
        "TransitionBack": Notificator.onTransitionBackMouseLeave,
        "TransitionLeft": Notificator.onTransitionLeftMouseLeave,
        "TransitionRight": Notificator.onTransitionRightMouseLeave,
        "TransitionUpRight": Notificator.onTransitionUpRightMouseLeave,
        "TransitionUpLeft": Notificator.onTransitionUpLeftMouseLeave,
        "TransitionPuzzle": Notificator.onTransitionPuzzleMouseLeave,
        "Transition": Notificator.onTransitionMouseLeave
    }

    def __init__(self):
        super(Transition, self).__init__()

        self.hotspot = None
        pass

    def _restorePolygon(self, value):
        self.hotspot.setPolygon(value)
        pass

    def getHotSpot(self):
        return self.hotspot
        pass

    def _onInitialize(self, obj):
        super(Transition, self)._onInitialize(obj)

        self.hotspot = self.createChild("HotSpotPolygon")
        self.hotspot.setEventListener(onHandleMouseButtonEvent=self._onMouseButtonEvent,
                                      onHandleMouseEnter=self._onMouseEnter,
                                      onHandleMouseLeave=self._onMouseLeave,
                                      onHandleMouseButtonEventBegin=self._onMouseButtonEventBegin,
                                      onHandleMouseOverDestroy=self._onMouseOverDestroy)
        self.hotspot.enable()
        pass

    def _onActivate(self):
        super(Transition, self)._onActivate()
        pass

    def _onFinalize(self):
        super(Transition, self)._onFinalize()

        Mengine.destroyNode(self.hotspot)
        self.hotspot = None
        pass

    def _onUpdateEnable(self, value):
        Notification.notify(Notificator.onTransitionEnable, self.object, value)
        pass

    def __updateBlockOpen(self, value):
        Notification.notify(Notificator.onTransitionBlockOpen, self.object, value)
        pass

    def _updateInteractive(self, value):
        if value is True:
            self.hotspot.enable()
        else:
            self.hotspot.disable()
            pass
        pass

    def _onMouseButtonEvent(self, touchId, x, y, button, pressure, isDown, isPressed):
        SceneName = SceneManager.getCurrentSceneName()

        if TransitionManager.isValidTransition(self.object, SceneName) is False:
            return False
            pass

        if button == 0 and isDown is True:
            if ArrowManager.emptyArrowAttach() is False:
                Notification.notify(Notificator.onTransitionUse, self.object)
                return True
                pass
            else:
                Notification.notify(Notificator.onTransitionClick, self.object)
                return True
                pass
            pass

        return True
        pass

    def _onMouseButtonEventBegin(self, touchId, x, y, button, pressure, isDown, isPressed):
        SceneName = SceneManager.getCurrentSceneName()

        if TransitionManager.isValidTransition(self.object, SceneName) is False:
            return False
            pass

        if button == 0 and isDown is True:
            if ArrowManager.emptyArrowAttach() is False:
                Notification.notify(Notificator.onTransitionUseBegin, self.object)
                return False
                pass
            else:
                Notification.notify(Notificator.onTransitionClickBegin, self.object)
                return False
                pass
            pass

        return False
        pass

    def _onMouseEnter(self, x, y):
        SceneName = SceneManager.getCurrentSceneName()

        if TransitionManager.isValidTransition(self.object, SceneName) is False:
            return False
            pass

        if self.BlockOpen is True:
            return False
            pass

        Notification.notify(Notificator.onTransitionMouseEnter, self.object)

        Cursor = TransitionManager.getTransitionCursor(self.object, SceneName)

        if Cursor is None:
            return False
            pass

        TransitionNotificator = Transition.NotificatorTransitionEnterDict[Cursor]

        Notification.notify(TransitionNotificator, self.object)
        return False
        pass

    def _onMouseOverDestroy(self):
        self._mouseLeave()
        pass

    def _mouseLeave(self):
        Notification.notify(Notificator.onInteractionMouseLeave, self.object)

    def _onMouseLeave(self):
        SceneName = SceneManager.getCurrentSceneName()

        if TransitionManager.isValidTransition(self.object, SceneName) is False:
            return
            pass

        if self.BlockOpen is True:
            return
            pass

        Notification.notify(Notificator.onTransitionMouseLeave, self.object)

        Cursor = TransitionManager.getTransitionCursor(self.object, SceneName)

        if Cursor is None:
            return
            pass

        TransitionNotificator = Transition.NotificatorTransitionLeaveDict[Cursor]

        Notification.notify(TransitionNotificator, self.object)
        return
        pass

    def isMouseEnter(self):
        hotspot = self.getHotSpot()

        pickerOver = hotspot.isMousePickerOver()

        return pickerOver
        pass

    pass
