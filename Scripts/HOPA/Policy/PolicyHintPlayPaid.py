from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintPlayPaid(TaskAlias):

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        DemonHint = SystemHint.getHintObject()

        if DemonHint.isActive():
            hint = DemonHint.entity
            if SystemMonetization.isComponentEnable("Hint") is True:
                source.addScope(SystemMonetization.scopePayGold, descr="Hint", scopeSuccess=hint.scopeHintLogic)
            else:
                source.addTask("PolicyHintPlayDefault")
        else:
            Trace.log("Policy", 0, "PolicyHintPlayDefault: Demon Hint is not active")
            source.addTask("PolicyDummy")
