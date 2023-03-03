from Foundation.Task.TaskAlias import TaskAlias


class AliasInventorySlotsScrolling(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsScrolling, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.Count = params.get("Count", None)
        self.Coordination = params.get("Coordination", None)

    def _onGenerate(self, source):
        source.addTask("AliasInventoryScrolling", Coordination=self.Coordination, Inventory=self.object, Count=self.Count)
        return False
