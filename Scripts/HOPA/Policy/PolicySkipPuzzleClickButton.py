from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicySkipPuzzleClickButton(TaskAlias):
    def _onParams(self, params):
        super(PolicySkipPuzzleClickButton, self)._onParams(params)
        self.SkipPuzzle = DemonManager.getDemon("SkipPuzzle")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskButtonClick", Group=self.SkipPuzzle, ButtonName="Button_Skip")
        pass