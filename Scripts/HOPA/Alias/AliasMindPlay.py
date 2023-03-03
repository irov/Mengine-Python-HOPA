from Foundation.GuardBlockGame import GuardBlockGame
from Foundation.Task.TaskAlias import TaskAlias


class AliasMindPlay(TaskAlias):
    def _onParams(self, params):
        super(AliasMindPlay, self)._onParams(params)

        self.mindID = params.get("MindID")
        self.isZoom = params.get("isZoom", False)
        self.Static = params.get("Static")
        pass

    def _onGenerate(self, source):
        with GuardBlockGame(source) as tc:
            tc.addTask("TaskMindPlay", MindID=self.mindID, isZoom=self.isZoom, Static=self.Static)
