from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.Task import Task
from Foundation.TaskManager import TaskManager


class TaskEffectFittingInventoryReturnInventoryItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskEffectFittingInventoryReturnInventoryItem, self)._onParams(params)
        self.FittingInventory = params.get("FittingInventory")
        self.InventoryItem = params.get("InventoryItem")
        self.SlotID = params.get("SlotID", None)
        pass

    def _onRun(self):
        FittingInventoryEntity = self.FittingInventory.getEntity()
        slots = FittingInventoryEntity.getSlots()

        slot = slots[self.SlotID]

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        InventoryItemEntity = self.InventoryItem.getEntity()

        P0 = InventoryItemEntity.getCameraPosition(Camera)

        P1 = (P2.x, P0.y)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        InventoryItemEntity.setLocalPosition(P0)
        layer_InventoryItemEffect.addChild(InventoryItemEntity)

        scaleTo = DefaultManager.getDefaultFloat("InventoryItemScale", 1.0)

        length = Mengine.length_v2_v2(P0, P2)

        SpeedEffectFittingInventoryReturnInventoryItem = DefaultManager.getDefaultFloat(
            "SpeedEffectFittingInventoryReturnInventoryItem", 2000)
        SpeedEffectFittingInventoryReturnInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectFittingInventoryReturnInventoryItem
        # time *= 1000  # speed fix

        with TaskManager.createTaskChain(Cb=self._onReturnInventoryItemEffectComplete) as tc:
            with tc.addParallelTask(2) as (tc0, tc1):
                tc0.addTask("TaskNodeBezier2To", Node=InventoryItemEntity, Point1=P1, To=P2,
                            Speed=SpeedEffectFittingInventoryReturnInventoryItem)
                tc1.addTask("TaskNodeScaleTo", Node=InventoryItemEntity, To=(scaleTo, scaleTo, 1.0), Time=time)
                pass
            pass

        return False
        pass

    def _onReturnInventoryItemEffectComplete(self, isSkip):
        self.complete()
        pass

    pass
