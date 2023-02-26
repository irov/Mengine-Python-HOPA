from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from HOPA.CutSceneManager import CutSceneManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroPlayCutScene(MacroCommand):
    def _onValues(self, values):
        self.CutSceneName = values[0]
        self.CutSceneDemonName = 'CutScene'
        self.CutSceneSceneName = 'CutScene'
        self.Transition = False
        self.isFade = True

        param_num = len(values)

        if param_num > 1:
            self.CutSceneDemonName = values[1]

            if param_num > 2:
                self.CutSceneSceneName = values[2]

                if param_num > 3:
                    self.Transition = bool(values[3])

                    if param_num > 4:
                        self.isFade = bool(values[4])

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if not SceneManager.hasScene(self.CutSceneSceneName):
                self.initializeFailed("MacroPlayCutScene SceneManager: not found scene '{}'".format(self.CutSceneSceneName))

            if not DemonManager.hasDemon(self.CutSceneDemonName):
                self.initializeFailed("MacroPlayCutScene DemonManager: not found demon '{}'".format(self.CutSceneDemonName))

            if not CutSceneManager.hasScene(self.CutSceneName):
                self.initializeFailed("MacroPlayCutScene CutSceneManager: not found cut scene '{}'".format(self.CutSceneName))

    def _onGenerate(self, source):
        CutSceneGroupName = CutSceneManager.getGroup(self.CutSceneName)
        if CutSceneGroupName is None:
            return

        CutSceneGroup = GroupManager.getGroup(CutSceneGroupName)

        if CutSceneGroup is None or isinstance(CutSceneGroup, GroupManager.EmptyGroup):
            source.addDummy()
            return
        source.addTask("TaskCutScenePlay", CutSceneName=self.CutSceneName, CutSceneDemonName=self.CutSceneDemonName, CutSceneSceneName=self.CutSceneSceneName, Transition=self.Transition, isFade=self.isFade)