from Foundation.GroupManager import GroupManager
from HOPA.Entities.BoneBoard.BoneBoardManager import BoneBoardManager
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroAddBone(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        self.bone_item = values[1]
        pass

    def _onInitialize(self):
        pass

    def _onGenerate(self, source):
        SocketName = BoneBoardManager.getSocketName(self.bone_item)
        GroupName = "BonePlates"
        Object = GroupManager.getObject(GroupName, SocketName)
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        Quest = self.addQuest(source, "BoneAdd", SceneName=self.SceneName,
                              GroupName=GroupName, Object=Object, InventoryItem=InventoryItem)
        with Quest as tc_quest:
            tc_quest.addTask("TaskNotify", ID=Notificator.onBoneAdd, Args=(self.ItemName, self.bone_item))
            tc_quest.addTask("TaskSocketPlaceInventoryItem", Socket=Object,
                             InventoryItem=InventoryItem, Taken=False, Pick=True)
            tc_quest.addTask("TaskFunction", Fn=BoneBoardManager.delPrev, Args=(self.bone_item,))
