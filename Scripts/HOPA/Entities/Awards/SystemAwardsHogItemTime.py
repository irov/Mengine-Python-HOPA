from Foundation.System import System

from AwardsManager import AwardsManager

class SystemAwardsHogItemTime(System):
    def _onParams(self, params):
        super(SystemAwardsHogItemTime, self)._onParams(params)
        self._timeQueue = []
        self._completeFive = 0
        self._completeThree = 0
        self._showAward = False
        pass

    def _onSave(self):
        return (self._completeFive, self._completeThree, self._showAward)
        pass

    def _onLoad(self, data_save):
        self._completeFive, self._completeThree, self._showAward = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onHOGFoundItem, self.__onHOGFoundItem)
        self.addObserver(Notificator.onEnigmaStart, self.__onEnigmaStart)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)
        return True
        pass

    def _onStop(self):
        pass

    def __onHOGFoundItem(self, HOGItemName):
        self._timeQueue.append(Mengine.getTime())

        if len(self._timeQueue) == 5:
            tmp = self._timeQueue[4] - self._timeQueue[0]
            if tmp <= 5:
                self._completeFive = 5
                self._showAward = True
                pass
            self._timeQueue.pop(0)
            pass

        if len(self._timeQueue) >= 3:
            i = len(self._timeQueue) - 1
            tmp = self._timeQueue[i] - self._timeQueue[i - 2]
            if tmp <= 3:
                self._completeThree = 3
                self._showAward = True
                pass
            pass

        return False
        pass

    def __onEnigmaStart(self, enigmaName):
        self._timeQueue = []
        return False
        pass

    def __onSceneEnter(self, sceneName):
        if self._showAward is False:
            return False
            pass

        awardsId = AwardsManager.getHogItemTimeAwardID(self._completeFive)
        if awardsId is not None:
            Notification.notify(Notificator.onAwardsOpen, awardsId)
            pass

        awardsId = AwardsManager.getHogItemTimeAwardID(self._completeThree)
        if awardsId is not None:
            Notification.notify(Notificator.onAwardsOpen, awardsId)
            pass
        self._showAward = False
        return False
        pass

    pass
