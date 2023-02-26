from Foundation.Task.TaskAlias import TaskAlias

class AliasInventorySlotsScrolling(TaskAlias):
    def _onParams(self, params):
        super(AliasInventorySlotsScrolling, self)._onParams(params)
        self.Inventory = params.get("Inventory")
        self.Count = params.get("Count", None)
        self.Coordination = params.get("Coordination", None)
        pass

    def _onGenerate(self, source):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        SlotCount = self.Inventory.getParam("SlotCount")
        InventoryEntity = self.Inventory.getEntity()
        Slots = InventoryEntity.getSlots()
        RemoveSlotIndex = SlotCount - 1

        source.addTask("AliasInventoryScrolling", Coordination=self.Coordination, Inventory=self.object, Count=self.Count)

        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryRight", Value = False)
        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryShow", Value = False)
        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryLeft", Value = True)
        #        source.addTask("TaskMovieLastFrame", MovieName = "Movie_InventoryLeft", Value = False)
        #
        ##        source.addTask("TaskEnable", ObjectName = "Movie_InventoryLeft", Value = True)
        ##        source.addTask("TaskEnable", ObjectName = "Movie_InventoryShow", Value = False)
        #
        #        for i in xrange(0,self.Count):
        #            CurrentSlotIndex = CurrentSlotIndex-1
        #            with source.addParallelTask(2) as (movie, inventory):
        #                movie.addTask("TaskMoviePlay", MovieName = "Movie_InventoryLeft")
        #
        #                if Slots[0].item is not None:
        #                    inventory.addTask("TaskInventorySlotRemoveItem", Inventory = self.Inventory, SlotID = 0)
        #                    pass
        #                if Slots[RemoveSlotIndex].item is not None:
        #                    inventory.addTask("TaskInventorySlotRemoveItem", Inventory = self.Inventory, SlotID = RemoveSlotIndex)
        #                    pass
        #                inventory.addTask("TaskInventoryCurrentSlotIndex", Inventory = self.Inventory, Value = CurrentSlotIndex)
        #                inventory.addTask("TaskInventorySlotsShowInventoryItem", Inventory = self.Inventory, Except = self.Except)
        #                pass
        #            pass
        #
        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryLeft", Value = False)
        #        source.addTask("TaskEnable", ObjectName = "Movie_InventoryShow", Value = True)
        #        source.addTask("TaskMovieLastFrame", MovieName = "Movie_InventoryShow", Value = True)

        return False

    pass