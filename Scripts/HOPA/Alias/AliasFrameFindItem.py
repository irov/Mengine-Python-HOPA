from Foundation.Task.TaskAlias import TaskAlias

from HOPA.ItemManager import ItemManager

class AliasFrameFindItem(TaskAlias):
    def __init__(self):
        super(AliasFindItem, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasFindItem, self)._onParams(params)

        self.ItemName = params.get("ItemName")
        self.SceneName = params.get("SceneName")
        pass

    def _onGenerate(self, source):
        ItemObject = ItemManager.getItemObject(self.ItemName)

        source.addTask("TaskItemClick", Item=ItemObject)
        source.addTask("TaskItemPick", Item=ItemObject)
        source.addTask("TaskNotify", ID=Notificator.onItemPicked, Args=(ItemObject,))
        source.addTask("TaskNotify", ID=Notificator.onSoundEffectOnObject, Args=(ItemObject, "PickItem"))
        pass
    pass