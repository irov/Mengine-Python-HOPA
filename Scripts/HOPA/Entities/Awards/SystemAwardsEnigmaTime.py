from Foundation.System import System
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification

from AwardsManager import AwardsManager


class SystemAwardsEnigmaTime(System):
    def _onParams(self, params):
        super(SystemAwardsEnigmaTime, self)._onParams(params)
        self._timeStart = 0
        self._skipFlag = False
        self._completeHog = 0
        self._completeEnigma = 0
        self._showAward = False
        self.TimeLessThan = None
        pass

    def _onSave(self):
        return (self._completeHog, self._completeEnigma, self._showAward)
        pass

    def _onLoad(self, data_save):
        self._completeHog, self._completeEnigma, self._showAward = data_save
        pass

    def _onRun(self):
        self.TimeLessThan = AwardsManager.getEnigmaTimeLimit()

        self.addObserver(Notificator.onEnigmaStart, self.__onEnigmaStart)
        self.addObserver(Notificator.onEnigmaComplete, self.__onEnigmaComplete)
        self.addObserver(Notificator.onEnigmaSkip, self.__onEnigmaSkip)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)

        return True
        pass

    def _onStop(self):
        pass

    def __onEnigmaStart(self, enigmaName):
        self._timeStart = 0
        self._timeStart = Mengine.getTime()

        return False
        pass

    def __onSceneEnter(self, sceneName):
        if self._showAward is False:
            return False
            pass

        awardsId = AwardsManager.getEnigmaTimeAwardID(self._completeHog)
        if awardsId is None:
            pass
        else:
            Notification.notify(Notificator.onAwardsOpen, awardsId)

        awardsId = AwardsManager.getEnigmaTimeAwardID(self._completeEnigma)
        if awardsId is None:
            pass
        else:
            Notification.notify(Notificator.onAwardsOpen, awardsId)
        self._showAward = False
        return False
        pass

    def __onEnigmaComplete(self, enigmaObject):
        if self._skipFlag is True:
            return False
            pass
        timeDiff = abs(self._timeStart - Mengine.getTime())
        if timeDiff >= self.TimeLessThan:
            return False
            pass

        EnigmaName = EnigmaManager.getEnigmaName(enigmaObject)
        enigma = EnigmaManager.getEnigma(EnigmaName)
        enigmaType = enigma.getType()
        if enigmaType == "HOGRolling":
            self._completeHog += 1
            self._showAward = True
            return False
            pass
        else:
            self._completeEnigma += 2
            self._showAward = True
            return False
            pass

        return False

    def __onEnigmaSkip(self):
        self._skipFlag = True
        return False
