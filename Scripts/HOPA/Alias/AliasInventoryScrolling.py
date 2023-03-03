from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryScrolling(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryScrolling, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.InventoryItem = params.get("InventoryItem", None)
        self.Count = params.get("Count", 1)
        self.Coordination = params.get("Coordination")
        self.ExceptSlots = params.get("ExceptSlots", [])

    def _onGenerate(self, source):
        InventoryEntity = self.Inventory.getEntity()
        InventoryEntity.scrollingCounts(self.Coordination, self.ExceptSlots, self.Count, self.InventoryItem)

        def __filterInvItem(inventory, invItem):
            if invItem is not self.InventoryItem:
                return False

            return True

        source.addTask("TaskListener", ID=Notificator.onInventoryReady, Filter=__filterInvItem)
