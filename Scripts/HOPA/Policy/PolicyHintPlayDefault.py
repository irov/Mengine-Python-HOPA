from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintPlayDefault(TaskAlias):

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        DemonHint = SystemHint.getHintObject()

        if DemonHint.isActive():
            hint = DemonHint.entity
            source.addScope(hint.scopeHintLogic)
        else:
            Trace.log("Policy", 0, "PolicyHintPlayDefault: Demon Hint is not active")
            source.addTask("PolicyDummy")