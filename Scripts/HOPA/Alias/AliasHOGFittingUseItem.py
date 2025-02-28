from Foundation.Notificator import Notificator
from Foundation.Task.TaskAlias import TaskAlias


class AliasHOGFittingUseItem(TaskAlias):
    def __init__(self):
        super(AliasHOGFittingUseItem, self).__init__()

    def _onParams(self, params):
        super(AliasHOGFittingUseItem, self)._onParams(params)
        self.ItemObject = params.get("ItemObject")
        self.ItemUseObject = params.get("ItemUseObject")

    def _onInitialize(self):
        super(AliasHOGFittingUseItem, self)._onInitialize()

    def _onGenerate(self, source):
        source.addTask("TaskItemClick", Item=self.ItemObject)
        source.addTask("TaskItemPick", Item=self.ItemObject)
        source.addNotify(Notificator.onItemPicked, self.ItemObject)
        source.addNotify(Notificator.onSoundEffectOnObject, self.ItemObject, "PickItem")
