from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroShowTutorial(MacroCommand):
    def _onValues(self, values):
        self.TutorialName = values[0]

    def _onInitialize(self):
        Tutorial = GroupManager.getGroup("Tutorial")

        if _DEVELOPMENT is True:
            if GroupManager.hasGroup("Tutorial") is False:
                self.initializeFailed("Tutorial group not found")

            if Tutorial.hasObject("Demon_Tutorial") is False:
                self.initializeFailed("Tutorial group not have Demon_Tutorial")

        self.Demon_Tutorial = Tutorial.getObject("Demon_Tutorial")

        if _DEVELOPMENT is True:
            if self.Demon_Tutorial.hasObject("Sprite_%s" % (self.TutorialName)) is False:
                self.initializeFailed("Tutorial:Demon_Tutorial not found Sprite_%s" % (self.TutorialName))

            if self.Demon_Tutorial.hasObject("Text_%s" % (self.TutorialName)) is False:
                self.initializeFailed("Tutorial:Demon_Tutorial not found Text_%s" % (self.TutorialName))

    def _onGenerate(self, source):
        source.addTask("TaskTutorialShow", Tutorial=self.Demon_Tutorial, TutorialName=self.TutorialName, TutorialSceneName=self.SceneName)