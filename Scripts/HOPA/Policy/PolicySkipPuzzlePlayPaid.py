from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicySkipPuzzlePlayPaid(TaskAlias):

    def _scopeSuccess(self, source):
        source.addTask("PolicySkipPuzzlePlayDefault")

    def _onGenerate(self, source):
        SystemMonetization = SystemManager.getSystem("SystemMonetization")

        if SystemMonetization.isComponentEnable("SkipPuzzle") is True:
            source.addScope(SystemMonetization.scopePayGold, descr="SkipPuzzle", scopeSuccess=self._scopeSuccess)
        else:
            source.addScope(self._scopeSuccess)
