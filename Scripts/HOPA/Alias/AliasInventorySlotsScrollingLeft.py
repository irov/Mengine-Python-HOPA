from Foundation.Task.TaskAlias import TaskAlias


class AliasInventorySlotsScrollingLeft(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsScrollingLeft, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.Count = params.get("Count", None)
        self.Except = params.get("Except", None)
        pass

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        SlotCount = self.Inventory.getParam("SlotCount")
        InventoryEntity = self.Inventory.getEntity()
        Slots = InventoryEntity.getSlots()
        RemoveSlotIndex = SlotCount - 1

        source.addTask("TaskEnable", ObjectName="Movie_InventoryRight", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie_InventoryShow", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie_InventoryLeft", Value=True)
        source.addTask("TaskMovieLastFrame", MovieName="Movie_InventoryLeft", Value=False)

        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryLeft", Value = True)
        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryShow", Value = False)

        for i in xrange(0, self.Count):
            CurrentSlotIndex = CurrentSlotIndex - 1
            with source.addParallelTask(2) as (movie, inventory):
                movie.addTask("TaskMoviePlay", MovieName="Movie_InventoryLeft")

                if Slots[0].item is not None:
                    inventory.addTask("TaskInventorySlotRemoveItem", Inventory=self.Inventory, SlotID=0)
                    pass
                if Slots[RemoveSlotIndex].item is not None:
                    inventory.addTask("TaskInventorySlotRemoveItem", Inventory=self.Inventory, SlotID=RemoveSlotIndex)
                    pass
                inventory.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=CurrentSlotIndex)
                inventory.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory, Except=self.Except)
                pass
            pass

        source.addTask("TaskEnable", ObjectName="Movie_InventoryLeft", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie_InventoryShow", Value=True)
        source.addTask("TaskMovieLastFrame", MovieName="Movie_InventoryShow", Value=True)

        return False

    pass
