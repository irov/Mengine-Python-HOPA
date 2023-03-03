from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasEnergyConsume(TaskAlias):

    def _onParams(self, params):
        self.Action = params["Action"]

        self.Cb = params.get("Cb")
        self.ScopeCb = params.get("ScopeCb")
        self.CbArgs = params.get("CbArgs", [])

        self.FailCb = params.get("FailCb")
        self.FailScopeCb = params.get("FailScopeCb")
        self.FailCbArgs = params.get("FailCbArgs", [])

    def _scopeCallback(self, source, status):
        if status == "success":
            scope, callback, args = self.ScopeCb, self.Cb, self.CbArgs
        elif status == "fail":
            scope, callback, args = self.FailScopeCb, self.FailCb, self.FailCbArgs
        else:
            return

        if scope is not None:
            source.addScope(scope, *args)
        elif callback is not None:
            source.addFunction(callback, *args)
        else:
            source.addDummy()

    def _onGenerate(self, source):
        if SystemManager.hasSystem("SystemEnergy") is False:
            source.addScope(self._scopeCallback, "success")
            return

        SystemEnergy = SystemManager.getSystem("SystemEnergy")

        if SystemEnergy.performAction(self.Action) is True:
            source.addScope(self._scopeCallback, "success")
        else:
            source.addScope(self._scopeCallback, "fail")
