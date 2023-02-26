from Foundation.Task.TaskAlias import TaskAlias

class AliasHOGInventoryFittingAddItem(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGInventoryFittingAddItem, self)._onParams(params)

        # self.Inventory = DemonManager.getDemon("HOGInventoryFitting")
        self.ItemName = params.get("ItemName")
        self.Enigma = params.get("Enigma")

        self.ItemObject = params.get("ItemObject")
        self.InventoryItemObject = params.get("InventoryItemObject")

        pass

    def _onGenerate(self, source):
        EnigmaEntity = self.Enigma.getEntity()
        Inventory = EnigmaEntity.getInventory()

        def addItemToSlotObjVis():
            self.Enigma.appendParam("Items", self.ItemName)
            pass

        source.addTask("AliasHOGFittingMoveItemToSlot", Inventory=Inventory, ItemName=self.ItemName, ItemObject=self.ItemObject, InventoryItemObject=self.InventoryItemObject)
        source.addTask("TaskFunction", Fn=addItemToSlotObjVis)
        pass

    pass