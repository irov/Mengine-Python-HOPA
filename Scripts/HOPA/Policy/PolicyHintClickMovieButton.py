from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintClickMovieButton(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintClickMovieButton, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        DemonHint = SystemHint.getHintObject()
        Button_Hint = DemonHint.getObject("Movie2Button_Hint")

        source.addTask("TaskMovie2ButtonClick", Movie2Button=Button_Hint)
