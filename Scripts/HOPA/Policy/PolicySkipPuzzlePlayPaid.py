from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicySkipPuzzlePlayPaid(TaskAlias):
    default_policy_name = "PolicySkipPuzzlePlayDefault"

    def _onGenerate(self, source):
        SystemMonetization = SystemManager.getSystem("SystemMonetization")

        if SystemMonetization.isComponentEnable("SkipPuzzle") is False:
            source.addTask(self.default_policy_name)
            return

        skip_puzzle_component = SystemMonetization.getComponent("SkipPuzzle")
        source.addScope(skip_puzzle_component.scopeActivate, self.default_policy_name)
