from Foundation.Task.TaskAlias import TaskAlias

class AliasInventoryPickInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryPickInventoryItem, self)._onParams(params)
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskEffectInventoryPickInventoryItem", InventoryItem=self.InventoryItem)
        pass

    pass