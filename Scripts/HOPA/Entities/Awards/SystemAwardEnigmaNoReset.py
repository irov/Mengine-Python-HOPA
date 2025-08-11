from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.Object.ObjectHOGRolling import ObjectHOGRolling

from AwardsManager import AwardsManager

class SystemAwardEnigmaNoReset(System):
    def _onParams(self, params):
        super(SystemAwardEnigmaNoReset, self)._onParams(params)
        self._resetCount = 0
        self._completeCount = 0
        self._showAward = False
        self.ButtonsLayerName = "PuzzleButtons"  # from ObjectPuzzleButtons
        pass

    def _onSave(self):
        return (self._resetCount, self._completeCount, self._showAward)
        pass

    def _onLoad(self, data_save):
        self._resetCount, self._completeCount, self._showAward = data_save
        pass

    def _onRun(self):
        self.addObserver(Notificator.onEnigmaComplete, self.__onEnigmaComplete)
        self.addObserver(Notificator.onEnigmaReset, self.__onEnigmaReset)
        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)

        return True
        pass

    def _onStop(self):
        if TaskManager.existTaskChain("PuzzleNoResetComplete"):
            TaskManager.cancelTaskChain("PuzzleNoResetComplete")
            pass
        pass

    def __onSceneEnter(self, sceneName):
        if self._showAward is False:
            return False
            pass

        count = self._completeCount
        awardsId = AwardsManager.getAwardWithResetCount(count)
        if awardsId is None:
            return False
            pass

        Notification.notify(Notificator.onAwardsOpen, awardsId)
        self._showAward = False
        return False
        pass

    def __onEnigmaComplete(self, enigmaObject):
        if isinstance(enigmaObject, ObjectHOGRolling):
            return False
            pass

        reset_interface = self.hasReset()
        if self._resetCount == 0 and reset_interface is True:
            self._showAward = True
            self._completeCount += 1
        else:
            self._showAward = False
        self._resetCount = 0
        return False
        pass

    def __onEnigmaReset(self):
        self._resetCount += 1
        return False
        pass

    def hasReset(self):
        SceneName = SceneManager.getCurrentSceneName()
        Slot = SceneManager.getSceneDescription(SceneName)
        groupName = Slot.getSlotsGroup(self.ButtonsLayerName)  # None or Group Name
        GroupNamesWithReset = AwardsManager.getAwardResetGroups()
        withReset = groupName in GroupNamesWithReset  # boolean
        return withReset
        pass

    pass
