from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.PuzzleRulesManager import PuzzleRulesManager


class PuzzleRules(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction("PuzzleName", Update=PuzzleRules._updatePuzzleName)
        pass

    def __init__(self):
        super(PuzzleRules, self).__init__()
        self.isPlay = False
        pass

    def _updatePuzzleName(self, value):
        if value is None:
            return

        self._showPuzzleRules()
        pass

    def _showPuzzleRules(self):
        self.isPlay = True
        if PuzzleRulesManager.hasPuzzleRules(self.PuzzleName) is False:
            Trace.log("Entity", 0, "PuzzleRules _onActivate: PuzzleRulesManager has not PuzzleRules with name %s" % (self.PuzzleName))
            pass

        Difficulty = Mengine.getCurrentAccountSetting("Difficulty")
        self.PuzzleRules = PuzzleRulesManager.getPuzzleRules(self.PuzzleName)

        if Difficulty is "Expert":
            self.textID = self.PuzzleRules.expertTextID
        else:
            self.textID = self.PuzzleRules.casualTextID
            pass

        self.textRules = self.object.getObject("Text_Rules")
        self.textRules.setTextID(self.textID)
        self.textRules.setEnable(False)

        with TaskManager.createTaskChain(Name="ShowPuzzleRules", Group=self.object) as tc:
            tc.addTask("TaskSocketClick", SocketName="Socket_ShowRules")
            tc.addEnable(self.textRules)
            tc.addTask("TaskEnable", ObjectName="Text_Default", Value=False)
            pass
        pass

    def _onDeactivate(self):
        self.isPlay = False

        if TaskManager.existTaskChain("ShowPuzzleRules"):
            TaskManager.cancelTaskChain("ShowPuzzleRules")
            pass
        pass

    pass
