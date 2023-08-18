from Foundation.Task.Task import Task
from Foundation.DemonManager import DemonManager
from Foundation.DefaultManager import DefaultManager
from Foundation.TaskManager import TaskManager


class PolicyTransitionAdvertising(Task):

    def _onParams(self, params):
        self.TransitionData = params
        self.AdvertDemonName = DefaultManager.getDefault("AdvertisingDemonName", default="AdvertisingScene")

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if DemonManager.hasDemon(self.AdvertDemonName) is False:
                self.initializeFailed("not found demon {} - check Config or Demons.xlsx".format(self.AdvertDemonName))
                return False

        return True

    def _onRun(self):
        transition_params = self.TransitionData
        demon = DemonManager.getDemon(self.AdvertDemonName)

        demon.setTransitionData(transition_params)
        if demon.runAdvertTransition(self._cbTransition) is False:
            # default transition, if advert failed
            TaskManager.runAlias("AliasTransition", self._cbTransition, **transition_params)

        return False

    def _cbTransition(self, isSkip):
        self.complete(isSkiped=isSkip)

