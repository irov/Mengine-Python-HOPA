from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.TaskAlias import TaskAlias

class AliasInventoryFindItem(MixinItem, TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryFindItem, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskItemClick", Item=self.Item)
        source.addTask("TaskItemPick", Item=self.Item)
        source.addTask("TaskInventoryAddItem", ItemName=self.ItemName)
        pass
    pass