from Foundation.System import System

from HOPA.NewspaperManager import NewspaperManager

class SystemAwardAllNewspapers(System):
    def _onParams(self, params):
        super(SystemAwardAllNewspapers, self)._onParams(params)
        self._newsCount = 0
        self._checkCount = NewspaperManager.getNewspapersCount()
        self._showAward = True
        pass

    def _onSave(self):
        return (self._newsCount, self._showAward)
        pass

    def _onLoad(self, data_save):
        self._newsCount, self._showAward = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onNewspaperShow, self.__onNewspaperShow)

        return True
        pass

    def _onStop(self):
        pass

    def __onNewspaperShow(self, newspaperId):
        self._newsCount += 1

        if self._showAward is False:
            return False
            pass

        if self._newsCount == self._checkCount:
            awardsId = "ID_Photo"
            Notification.notify(Notificator.onAwardsOpen, awardsId)
            self._showAward = False
            pass

        return False
