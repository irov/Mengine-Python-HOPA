from Foundation.SessionManager import SessionManager
from Foundation.System import System

class SystemWalktrhough(System):
    def _onParams(self, params):
        super(SystemWalktrhough, self)._onParams(params)
        pass

    def _onRun(self):
        self.addObserver(Notificator.onKeyEvent, self.__onKeyEvent)
        pass

    def _onStop(self):
        pass

    def __onKeyEvent(self, key, x, y, isDown, isRepeating):
        if key == Mengine.KC_Q and isDown is True:
            SessionManager.removeCurrentSession()
            SessionManager.startWalktrhough()
            pass

        return False
        pass

    pass