from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.Task import Task
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager

class TaskEffectFittingInventoryAddInventoryItem(Task):
    def _onParams(self, params):
        super(TaskEffectFittingInventoryAddInventoryItem, self)._onParams(params)
        self.FittingInventory = params.get("FittingInventory")
        self.ItemName = params.get("ItemName")
        self.SlotID = params.get("SlotID", None)
        self.item = None
        pass

    def _onRun(self):
        self.item = ItemManager.getItemObject(self.ItemName)
        self.itemEntity = self.item.getEntity()

        inventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        inventoryItemEntity = inventoryItem.getEntity()

        Camera = Mengine.getRenderCamera2D()
        P2 = inventoryItemEntity.getCameraPosition(Camera)

        P0 = self.itemEntity.getCameraPosition(Camera)
        P1 = (P2.x, P0.y)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(self.itemEntity)
        self.itemEntity.setLocalPosition(P0)
        self.itemEntity.enable()

        sprite = self.itemEntity.getSprite()
        size = sprite.getSurfaceSize()

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        scaleToX = InventorySlotSize / size.x
        scaleToY = InventorySlotSize / size.y

        scaleTo = min(scaleToX, scaleToY)

        length = Mengine.length_v2_v2(P1, P2)
        SpeedEffectFittingInventoryAddItem = DefaultManager.getDefaultFloat("SpeedEffectFittingInventoryAddItem", 2000)
        SpeedEffectFittingInventoryAddItem *= 0.001  # speed fix
        time = length * 1.3 / SpeedEffectFittingInventoryAddItem
        # time *= 1000  # speed fix

        with TaskManager.createTaskChain(Cb=self._onEffectInventoryAddItemComplete) as tc:
            with tc.addParallelTask(3) as (tcp0, tcp1, tcp2):
                tcp0.addTask("TaskNodeBezier2To", Node=self.itemEntity, Point1=P1, To=P2, Speed=SpeedEffectFittingInventoryAddItem)
                tcp1.addTask("TaskNodeScaleTo", Node=self.itemEntity, To=(scaleTo, scaleTo, 1.0), Time=time)
                tcp2.addTask("TaskDelay", Time=time / 2)
                tcp2.addTask("TaskNodeAlphaTo", Node=self.itemEntity, To=0.3, Time=time / 2)
                pass
            pass

        return False
        pass

    def _onEffectInventoryAddItemComplete(self, isSkip):
        self.itemEntity.setLocalPosition((0, 0))
        self.itemEntity.disable()
        self.item.setEnable(False)

        self.complete()
        pass

    pass