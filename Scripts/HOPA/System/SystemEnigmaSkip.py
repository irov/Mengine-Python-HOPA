from Foundation.DefaultManager import DefaultManager
from Foundation.Notificator import Notificator
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Notification import Notification

class SystemEnigmaSkip(System):
    def _onParams(self, params):
        super(SystemEnigmaSkip, self)._onParams(params)
        pass

    def _onRun(self):
        self.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)

        return True
        pass

    def _onStop(self):
        pass

    @staticmethod
    def __onKeyEvent(key, x, y, isDown, isRepeating):
        if isDown is False:
            return False

        if isRepeating:
            return False

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return False

        if key == DefaultManager.getDefaultKey("DevDebugSkipEnigma", "VK_SPACE"):
            Notification.notify(Notificator.onEnigmaSkip)
            Notification.notify(Notificator.onShiftCollectSkip)

        return False