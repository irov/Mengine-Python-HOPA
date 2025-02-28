from Foundation.TaskManager import TaskManager

from Notification import Notification


class RotateAndSwapChipsSlotController(object):
    def __init__(self, slot, deltaAngle, buttonObject):
        self.slot = slot
        self.buttonObject = buttonObject
        self.buttonObject.setInteractive(True)
        self.button = self.buttonObject.getEntity()
        self.deltaAngle = deltaAngle
        self.onAction = False
        self.taskName = "RotateAndSwapChipsSlotController_Rotate_" + self.buttonObject.getName()
        self.observerClick = None
        self.observerClickEnd = None
        pass

    def initialize(self):
        self.globalHandleMouseButtonEvent = Mengine.addMouseButtonHandler(self._onGlobalMouseButtonEvent)

        self.observerClick = Notification.addObserver(Notificator.onButtonClick, self._onButtonClick)
        self.observerClickEnd = Notification.addObserver(Notificator.onButtonClickEndUp, self._onButtonClickEndUp)
        pass

    def _onButtonClick(self, button):
        if button != self.buttonObject:
            return False
            pass

        if self.onAction is True:
            return False
            pass

        self.onAction = True
        self.startRotation()
        return False
        pass

    def _onGlobalMouseButtonEvent(self, event):
        if event.isDown is True:
            return
            pass

        if self.onAction is False:
            return
            pass

        self.onAction = False

        self.stopRotation()
        pass

    def _onButtonClickEndUp(self, button):
        if button != self.buttonObject:
            return False
            pass

        if self.onAction is False:
            return False
            pass

        self.onAction = False
        self.stopRotation()
        return False
        pass

    def startRotation(self):
        Mengine.enableGlobalHandler(self.globalHandleMouseButtonEvent, True)

        self.slot.startRotation()
        if TaskManager.existTaskChain(self.taskName) is True:
            TaskManager.cancelTaskChain(self.taskName)
            pass

        with TaskManager.createTaskChain(Name=self.taskName, Group=None, Repeat=True) as tc:
            # tc.addTask("TaskMovieLastFrame", MovieName = name, Value = False)
            tc.addFunction(self.rotateSlot)
            tc.addDelay(0.1 * 1000)  # speed fix
            pass
        pass

    def stopRotation(self):
        self.slot.stopRotation()

        Mengine.enableGlobalHandler(self.globalHandleMouseButtonEvent, False)

        if TaskManager.existTaskChain(self.taskName) is False:
            return
            pass

        TaskManager.cancelTaskChain(self.taskName)
        chip = self.slot.getChip()
        Notification.notify(Notificator.onPlaceChip, chip)
        pass

    def rotateSlot(self):
        self.slot.rotate(self.deltaAngle)
        pass

    def finalize(self):
        Mengine.removeGlobalHandler(self.globalHandleMouseButtonEvent)
        self.globalHandleMouseButtonEvent = None

        Notification.removeObserver(self.observerClick)
        Notification.removeObserver(self.observerClickEnd)
        pass

    pass
