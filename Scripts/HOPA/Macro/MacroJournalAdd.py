from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroJournalAdd(MacroCommand):
    def _onValues(self, values):
        self.ItemObjectName = None
        self.JournalID = values[0]

        if len(values) < 2:
            return
            pass

        self.ItemObjectName = values[1]
        pass

    #    def _onInitialize(self, **params):
    #        if self.ItemName is None:
    #            self.initializeFailed("Item is None")
    #            pass
    #
    #        if ItemManager.hasItemInventoryItem(self.ItemName) is False:
    #            self.initializeFailed("Item %s not have InventoryName"%(self.ItemName))
    #            pass
    #        pass

    def _onGenerate(self, source):
        Journal = DemonManager.getDemon("Journal")

        if self.ItemObjectName is not None:
            ItemObject = GroupManager.getObject(self.GroupName, self.ItemObjectName)
            source.addTask("AliasJournalAddItemPage", ItemObject=ItemObject, SceneName=self.SceneName)
            pass

        source.addNotify(Notificator.onJournalAddPage, self.JournalID)
        pass

    pass
