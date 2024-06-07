from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintPlayPaid(TaskAlias):
    default_policy_name = "PolicyHintPlayDefault"

    def _onGenerate(self, source):
        SystemMonetization = SystemManager.getSystem("SystemMonetization")

        if SystemMonetization.isComponentEnable("Hint") is False:
            source.addTask(self.default_policy_name)
            return

        hint_component = SystemMonetization.getComponent("Hint")
        source.addScope(hint_component.scopeActivate, self.default_policy_name)
