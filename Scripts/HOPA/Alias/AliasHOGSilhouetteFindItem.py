from Foundation.Task.TaskAlias import TaskAlias
from HOPA.EnigmaManager import EnigmaManager
from HOPA.HOGManager import HOGManager
from HOPA.QuestManager import QuestManager


class AliasHOGSilhouetteFindItem(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGSilhouetteFindItem, self)._onParams(params)
        self.HOG = params.get("HOG")
        self.HOGItemName = params.get("HOGItemName")
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        SceneName = EnigmaManager.getEnigmaSceneName(self.EnigmaName)
        GroupName = EnigmaManager.getEnigmaGroupName(self.EnigmaName)
        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        ItemName = hogItem.objectName

        ItemObject = self.Group.getObject(ItemName)
        ObjectType = ItemObject.getType()

        Quest = QuestManager.createLocalQuest("HOGPickItem", SceneName=SceneName, GroupName=GroupName,
                                              HogGroupName=self.GroupName, ItemName=ItemName, HogItem=hogItem)
        with QuestManager.runQuest(source, Quest) as tc_quest:
            if ObjectType is "ObjectMovieItem" or ObjectType is "ObjectMovie2Item":
                tc_quest.addTask("TaskMovieItemClick", MovieItem=ItemObject)
            else:
                tc_quest.addTask("TaskItemClick", ItemName=ItemName)

        if ObjectType is "ObjectMovieItem" or ObjectType is "ObjectMovie2Item":
            source.addTask("TaskMovieItemPick", MovieItem=ItemObject)

        source.addTask("TaskItemPick", ItemName=ItemName)
        source.addTask("TaskNotify", ID=Notificator.onHOGItemPicked)
        source.addTask("AliasHOGSilhouetteFoundItem", HOG=self.HOG, HOGItemName=self.HOGItemName,
                       EnigmaName=self.EnigmaName)
