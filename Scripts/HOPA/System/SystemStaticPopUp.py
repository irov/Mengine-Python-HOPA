from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from HOPA.StaticPopUpManager import StaticPopUpManager
from HOPA.StaticPopUpTransitionManager import StaticPopUpTransitionManager
from Notification import Notification


class SystemStaticPopUp(System):
    def _onParams(self, params):
        super(SystemStaticPopUp, self)._onParams(params)
        self.ShowObservers = params.get("ShowObserversID")
        self.HideObservers = params.get("HideObserversID")
        self.DisableObservers = params.get("DisableObserversID")
        self.object = None
        self.listObservers = []
        pass

    def _onRun(self):
        for observerID in self.ShowObservers:
            observer = Notification.addObserver(observerID, self.__showStaticPopUp)
            self.listObservers.append(observer)
            pass

        for observerID in self.HideObservers:
            observer = Notification.addObserver(observerID, self.__hideStaticPopUp)
            self.listObservers.append(observer)
            pass

        for observerID in self.DisableObservers:
            observer = Notification.addObserver(observerID, self._disableStaticPopUp)
            self.listObservers.append(observer)
            pass
        pass

    def _onStop(self):
        for observer in self.listObservers:
            Notification.removeObserver(observer)
            pass

        self.listObservers = []

        self.object = None
        pass

    def __showStaticPopUp(self, object):
        StaticPopUp = DemonManager.getDemon("StaticPopUp")
        StaticPopUpEntity = StaticPopUp.getEntity()
        ForeignKey = StaticPopUpManager.hasForeignKey(object)
        if ForeignKey is True:
            sceneName = SceneManager.getCurrentSceneName()
            textID = StaticPopUpTransitionManager.getTextId(sceneName)
            pass
        else:
            textID = StaticPopUpManager.findTextID(object)
            pass

        if textID is None:
            return False

        if self.object is not None:
            self.__hideStaticPopUp(self.object)
            pass

        self.object = object
        StaticPopUpEntity.show(textID)
        return False
        pass

    def __hideStaticPopUp(self, object):
        StaticPopUp = DemonManager.getDemon("StaticPopUp")
        StaticPopUpEntity = StaticPopUp.getEntity()

        if self.object is not object:
            return False
            pass

        self.object = None

        StaticPopUpEntity.hide()

        return False
        pass

    def _disableStaticPopUp(self, object):
        StaticPopUp = DemonManager.getDemon("StaticPopUp")
        StaticPopUpEntity = StaticPopUp.getEntity()

        StaticPopUpEntity.disable()
        pass

    pass
