from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from HOPA.ItemManager import ItemManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroOpenItemPlus(MacroCommand):
    def _onValues(self, values):
        self.ItemName = values[0]
        self.ScenePlus = None

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            if ItemManager.hasItem(self.ItemName) is False:
                self.initializeFailed("Item %s not found" % self.ItemName)

        itemInManager = ItemManager.getItem(self.ItemName)
        self.ScenePlus = itemInManager.PlusScene

        if _DEVELOPMENT is True:
            if self.ScenePlus is None:
                self.initializeFailed("Item %s not has ScenePlus" % self.ItemName)

            if GroupManager.hasGroup(self.ScenePlus) is False:
                self.initializeFailed("Not found group" % self.ScenePlus)

    def _onGenerate(self, source):
        GroupZoom = GroupManager.getGroup(self.ScenePlus)

        Quest = self.addQuest(source, "EnterScene", SceneName=self.SceneName, GroupName=self.GroupName)

        with Quest as tc_quest:
            tc_quest.addTask("TaskNotify", ID=Notificator.onItemZoomEnter, Args=(GroupZoom, self.ScenePlus))
