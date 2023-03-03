from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias


class AliasInventoryCombineInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(AliasInventoryCombineInventoryItem, self)._onParams(params)
        self.Inventory = params.get("Inventory")

        self.AttachInventoryItem = params.get("AttachInventoryItem")
        self.SlotInventoryItem = params.get("SlotInventoryItem")

    def _onGenerate(self, source):
        source.addTask("TaskInventoryCombineInventoryItem", Inventory=self.Inventory,
                       AttachInventoryItem=self.AttachInventoryItem, SlotInventoryItem=self.SlotInventoryItem)

        with GuardBlockInput(source) as guard_scope:
            guard_scope.addTask("TaskSoundEffect", SoundName="CombineSuccess", Wait=False)

            guard_scope.addTask("TaskRemoveArrowAttach")

            AttachInventoryItem = self.AttachInventoryItem
            SlotInventoryItem = self.SlotInventoryItem

            guard_scope.addTask("TaskSceneLayerAddEntity", LayerName="InventoryItemEffect",
                                Object=SlotInventoryItem, AdaptScreen=True)
            guard_scope.addTask("TaskSceneLayerAddEntity", LayerName="InventoryItemEffect",
                                Object=AttachInventoryItem, AdaptScreen=True)

            time = 1
            time *= 1000  # speed fix

            with guard_scope.addParallelTask(2) as (tc_item0, tc_item1):
                with tc_item0.addParallelTask(2) as (tc0, tc1):
                    tc0.addTask("AliasObjectMoveTo", Object=AttachInventoryItem, To=(512, 384), Time=time)
                    tc1.addTask("AliasObjectAlphaTo", Object=AttachInventoryItem, To=0.0, Time=time)

                with tc_item1.addParallelTask(2) as (tc0, tc1):
                    tc0.addTask("AliasObjectMoveTo", Object=SlotInventoryItem, To=(512, 384), Time=time)
                    tc1.addTask("AliasObjectAlphaTo", Object=SlotInventoryItem, To=0.0, Time=time)

            guard_scope.addTask("TaskObjectReturn", Object=AttachInventoryItem)
            guard_scope.addTask("TaskObjectReturn", Object=SlotInventoryItem)

            guard_scope.addTask("TaskEnable", Object=AttachInventoryItem, Value=False)
            guard_scope.addTask("TaskEnable", Object=SlotInventoryItem, Value=False)

            guard_scope.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)

            guard_scope.addTask("TaskDelParam", Object=self.Inventory, Param="InventoryItems", Value=self.AttachInventoryItem)
            guard_scope.addTask("TaskDelParam", Object=self.Inventory, Param="InventoryItems", Value=self.SlotInventoryItem)

            guard_scope.addTask("AliasInventoryShowCurrentSlots", Inventory=self.Inventory)

            guard_scope.addTask("TaskSoundEffect", SoundName="CombinedObject", Wait=False)
