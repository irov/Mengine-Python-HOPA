from Foundation.Task.TaskAlias import TaskAlias


class AliasInventorySlotsScrollingRight(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsScrollingRight, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.Count = params.get("Count", None)
        self.Except = params.get("Except", None)
        pass

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        SlotCount = self.Inventory.getParam("SlotCount")
        RemoveSlotIndex = SlotCount - 1
        InventoryEntity = self.Inventory.getEntity()
        Slots = InventoryEntity.getSlots()

        source.addTask("TaskNotify", ID=Notificator.onInventoryScrolling, Args=(self.Inventory,))
        source.addTask("TaskEnable", ObjectName="Movie_InventoryLeft", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie_InventoryShow", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie_InventoryRight", Value=True)
        source.addTask("TaskMovieLastFrame", MovieName="Movie_InventoryRight", Value=False)
        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryShow", Value = False)

        for i in xrange(0, self.Count):
            CurrentSlotIndex = CurrentSlotIndex + 1
            with source.addParallelTask(2) as (movie, inventory):
                movie.addTask("TaskMoviePlay", MovieName="Movie_InventoryRight")

                if Slots[RemoveSlotIndex].item is not None:
                    inventory.addTask("TaskInventorySlotRemoveItem", Inventory=self.Inventory, SlotID=RemoveSlotIndex)
                if Slots[0].item is not None:
                    inventory.addTask("TaskInventorySlotRemoveItem", Inventory=self.Inventory, SlotID=0)
                inventory.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=CurrentSlotIndex)
                inventory.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory, Except=self.Except)

        source.addTask("TaskEnable", ObjectName="Movie_InventoryRight", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie_InventoryShow", Value=True)
        source.addTask("TaskMovieLastFrame", MovieName="Movie_InventoryShow", Value=True)
