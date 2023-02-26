from Foundation.System import System
from Notification import Notification

from AwardsManager import AwardsManager

class SystemAwardGameComplete(System):
    def _onParams(self, params):
        super(SystemAwardGameComplete, self)._onParams(params)
        self._showAward = False
        pass

    def _onSave(self):
        return self._showAward
        pass

    def _onLoad(self, data_save):
        self._showAward = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onBonusGameComplete, self.__onGameComplete)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)
        return True
        pass

    def _onStop(self):
        pass

    def __onSceneEnter(self, sceneName):
        if self._showAward is False:
            return False
            pass

        difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        award = AwardsManager.getDiffAward(difficulty)
        if award is None:
            self._showAward = False
            return False
            pass

        Notification.notify(Notificator.onAwardsOpen, award)
        self._showAward = False
        return False
        pass

    def __onGameComplete(self):
        self._showAward = True
        return False
        pass

    pass