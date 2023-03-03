from Foundation.DemonManager import DemonManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.FittingInventoryManager import FittingInventoryManager
from HOPA.ItemManager import ItemManager


class AliasFittingFindItem(TaskAlias):
    def _onParams(self, params):
        super(AliasFittingFindItem, self)._onParams(params)

        self.ItemName = params.get("ItemName")
        self.SceneName = params.get("SceneName")
        pass

    def _onInitialize(self):
        super(AliasFittingFindItem, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        FittingInventory = DemonManager.getDemon("FittingInventory")
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        if FittingInventory.hasFitting(InventoryItem) == False:
            Slot = FittingInventoryManager.s_slots[self.ItemName]
            SlotIndex = Slot.getIndex()
            source.addTask("TaskFittingInventoryAddFitting", FittingInventory=FittingInventory,
                           SlotIndex=SlotIndex, InventoryItem=InventoryItem)

        ObjectItem = ItemManager.getItemObject(self.ItemName)

        #        Quest = QuestManager.createLocalQuest(source, "PickItem", self.SceneName, GroupName = self.GroupName, Item = ObjectItem)
        #        Quest = self.addQuest(source, "PickItem", SceneName = self.SceneName, GroupName = self.GroupName, ItemName = ObjectItem)
        #        with QuestManager.runQuest(source, Quest) as tc_quest:
        source.addTask("TaskItemClick", ItemName=ObjectItem.name)
        #            pass

        source.addTask("TaskSoundEffect", SoundName="ItemPicked", Wait=False)

        if ItemManager.hasItemInventoryItem(self.ItemName) is True:
            FittingInventory = DemonManager.getDemon("FittingInventory")

            source.addTask("AliasFittingInventoryAddInventoryItem", FittingInventory=FittingInventory,
                           ItemName=self.ItemName)
