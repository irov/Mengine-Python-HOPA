from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintClickButton(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintClickButton, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        DemonHint = SystemHint.getHintObject()
        source.addTask("TaskButtonClick", Group=DemonHint, ButtonName="Button_Hint")
        pass
    pass