from Foundation.Notificator import Notificator
from Foundation.Task.TaskAlias import TaskAlias

class AliasHOGFittingUseItem(TaskAlias):
    def __init__(self):
        super(AliasHOGFittingUseItem, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasHOGFittingUseItem, self)._onParams(params)
        self.ItemObject = params.get("ItemObject")
        self.ItemUseObject = params.get("ItemUseObject")
        pass

    def _onInitialize(self):
        super(AliasHOGFittingUseItem, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        source.addTask("TaskItemClick", Item=self.ItemObject)
        source.addTask("TaskItemPick", Item=self.ItemObject)
        source.addTask("TaskNotify", ID=Notificator.onItemPicked, Args=(self.ItemObject,))
        source.addTask("TaskNotify", ID=Notificator.onSoundEffectOnObject, Args=(self.ItemObject, "PickItem"))
        pass
    pass