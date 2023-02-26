from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.EnigmaManager import EnigmaManager
from Notification import Notification

from AwardsManager import AwardsManager

class SystemAwardNoSkip(System):
    def _onParams(self, params):
        super(SystemAwardNoSkip, self)._onParams(params)
        self._skipCount = 0
        self._completeCount = 0
        self._showAward = False
        pass

    def _onSave(self):
        return (self._skipCount, self._completeCount, self._showAward)
        pass

    def _onLoad(self, data_save):
        self._skipCount, self._completeCount, self._showAward = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onEnigmaComplete, self.__onEnigmaComplete)
        self.addObserver(Notificator.onEnigmaSkip, self.__onEnigmaSkip)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)

        return True
        pass

    def _onStop(self):
        if TaskManager.existTaskChain("PuzzleNoSkipComplete"):
            TaskManager.cancelTaskChain("PuzzleNoSkipComplete")
            pass
        pass

    def __onSceneEnter(self, sceneName):
        if self._showAward is False:
            return False
            pass

        count = self._completeCount - self._skipCount
        awardsId = AwardsManager.getNoSkipAwardID(count)
        if awardsId is None:
            return False
            pass

        Notification.notify(Notificator.onAwardsOpen, awardsId)
        self._showAward = False
        return False
        pass

    def __onEnigmaComplete(self, enigmaObject):
        EnigmaName = EnigmaManager.getEnigmaName(enigmaObject)
        enigma = EnigmaManager.getEnigma(EnigmaName)
        enigmaType = enigma.getType()
        if enigmaType == "HOGRolling":
            return False
            pass
        enigmaEntity = enigma.getEntity()
        if enigmaEntity.isSkiping() is True:
            return False
            pass
        self._completeCount += 1
        self._showAward = True
        return False
        pass

    def __onEnigmaSkip(self):
        self._skipCount += 1
        return False
        pass

    pass