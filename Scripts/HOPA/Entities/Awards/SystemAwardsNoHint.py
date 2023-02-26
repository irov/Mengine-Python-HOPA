from Foundation.System import System
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification

from AwardsManager import AwardsManager

class SystemAwardsNoHint(System):
    def _onParams(self, params):
        super(SystemAwardsNoHint, self)._onParams(params)
        self._hintClick = False
        self._completeCount = 0
        self._showAward = False
        pass

    def _onSave(self):
        return (self._completeCount, self._showAward)
        pass

    def _onLoad(self, data_save):
        self._completeCount, self._showAward = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onHintClick, self.__onHintClick)
        self.addObserver(Notificator.onEnigmaStart, self.__onEnigmaStart)
        self.addObserver(Notificator.onEnigmaComplete, self.__onEnigmaComplete)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)
        return True
        pass

    def _onStop(self):
        pass

    def __onSceneEnter(self, sceneName):
        if self._showAward is False:
            return False
            pass

        count = self._completeCount
        awardsId = AwardsManager.getNoHintAwardID(count)
        if awardsId is None:
            return False
            pass

        Notification.notify(Notificator.onAwardsOpen, awardsId)
        self._showAward = False
        return False
        pass

    def __onHintClick(self, hintObject, valid, *args):
        if valid is False:
            return False
            pass
        self._hintClick = True
        return False
        pass

    def __onEnigmaComplete(self, enigmaObject):
        EnigmaName = EnigmaManager.getEnigmaName(enigmaObject)
        enigma = EnigmaManager.getEnigma(EnigmaName)
        enigmaType = enigma.getType()

        if self._hintClick is True or enigmaType != "HOGRolling":
            return False
            pass

        self._completeCount += 1
        self._showAward = True
        return False
        pass

    def __onEnigmaStart(self, enigmaObject):
        self._hintClick = False
        return False
        pass

    pass