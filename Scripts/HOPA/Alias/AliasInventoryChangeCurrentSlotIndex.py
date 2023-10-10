from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias
# from HOPA.ItemManager import ItemManager


class AliasInventoryChangeCurrentSlotIndex(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryChangeCurrentSlotIndex, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
        self.NewSlotIndex = params.get("NewSlotIndex")
        pass

    def _onGenerate(self, source):
        # ItemObject = ItemManager.getItemObject(self.ItemName)
        with GuardBlockInput(source) as guard_source:
            # ---- cause this bug: https://wonderland-games.atlassian.net/browse/C1-29 ----
            # if ItemObject is not None:
            #     guard_source.addEnable(ItemObject)
            # -----------------------------------------------------------------------------
            guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)
            guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=self.NewSlotIndex)
            guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)
