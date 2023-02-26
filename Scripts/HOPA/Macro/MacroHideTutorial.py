from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroHideTutorial(MacroCommand):

    def _onInitialize(self):
        Tutorial = GroupManager.getGroup("Tutorial")

        if _DEVELOPMENT is True:
            if GroupManager.hasGroup("Tutorial") is False:
                self.initializeFailed("Tutorial group not found")

        if _DEVELOPMENT is True:
            if Tutorial.hasObject("Demon_Tutorial") is False:
                self.initializeFailed("Tutorial group not have Demon_Tutorial")

        self.Demon_Tutorial = Tutorial.getObject("Demon_Tutorial")

    def _onGenerate(self, source):
        source.addTask("TaskTutorialShow", Tutorial=self.Demon_Tutorial, TutorialName=None, TutorialSceneName=None)