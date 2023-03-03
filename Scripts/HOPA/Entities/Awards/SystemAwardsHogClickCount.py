from Foundation.System import System
from HOPA.Object.ObjectHOGRolling import ObjectHOGRolling
from Notification import Notification

from AwardsManager import AwardsManager


class SystemAwardsHogClickCount(System):
    def _onParams(self, params):
        super(SystemAwardsHogClickCount, self)._onParams(params)
        self._skipFlag = False
        self._completeHog = 0
        self._completeEnigma = 0
        self._showAward = False
        self.click_enumerator = 0
        self.currentRollingObject = None
        pass

    def _onSave(self):
        return (self._completeHog, self._completeEnigma, self._showAward)
        pass

    def _onLoad(self, data_save):
        self._completeHog, self._completeEnigma, self._showAward = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onEnigmaStart, self.__onEnigmaStart)
        self.addObserver(Notificator.onEnigmaComplete, self.__onEnigmaComplete)
        self.addObserver(Notificator.onEnigmaSkip, self.__onEnigmaSkip)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)
        self.addObserver(Notificator.onMouseButtonEvent, self.__clickCounter)

        return True
        pass

    def _onStop(self):
        pass

    def __clickCounter(self, event):
        if event.isDown is True:
            self.click_enumerator += 1
            pass

        return False
        pass

    def __onEnigmaStart(self, enigmaObject):
        if isinstance(enigmaObject, ObjectHOGRolling):
            self.currentRollingObject = enigmaObject
            pass

        self.click_enumerator = 0
        return False
        pass

    def __onSceneEnter(self, sceneName):
        if self._showAward is False:
            return False
            pass
        count = self._completeHog
        awardsId = AwardsManager.getEnigmaTimeAwardID(count)
        if awardsId is not None:
            Notification.notify(Notificator.onAwardsOpen, awardsId)
            pass

        awardsId = AwardsManager.getAwardWithClickCount(self._completeEnigma)

        if awardsId is not None:
            Notification.notify(Notificator.onAwardsOpen, awardsId)
            pass

        self._showAward = False
        return False
        pass

    def __onEnigmaComplete(self, enigmaObject):
        if self._skipFlag is True:
            return False
            pass

        if self.currentRollingObject is not enigmaObject:
            return False
            pass

        if self.currentRollingObject is None:
            return False
            pass

        items = self.currentRollingObject.getParam("FoundItems")
        countItems = len(items)
        if self.click_enumerator < countItems + 6:
            self._completeHog += 1
            self._showAward = True
            return False
            pass
        return False
        pass

    def __onEnigmaSkip(self):
        self._skipFlag = True
        self.click_enumerator = 0
        self.currentRollingObject = None
        return False
        pass

    pass
