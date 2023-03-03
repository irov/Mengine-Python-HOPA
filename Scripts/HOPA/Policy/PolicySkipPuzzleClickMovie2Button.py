from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicySkipPuzzleClickMovie2Button(TaskAlias):
    def _onParams(self, params):
        super(PolicySkipPuzzleClickMovie2Button, self)._onParams(params)
        self.SkipPuzzle = DemonManager.getDemon("SkipPuzzle")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskMovie2ButtonClick", Group=self.SkipPuzzle, Movie2ButtonName="Movie2Button_Skip")
        pass
