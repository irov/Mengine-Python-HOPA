from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias

class AliasTipPlay(MixinObject, TaskAlias):
    def _onParams(self, params):
        super(AliasTipPlay, self)._onParams(params)

        self.tipID = params.get("TipID")
        self.Notifies = params.get("Notifies", [])
        pass

    def _onGenerate(self, source):
        self.ObjectType = self.Object.getType()

        source.addTask("TaskTipPlay", Object=self.Object, TipID=self.tipID, Notifies=self.Notifies)
        pass
    pass