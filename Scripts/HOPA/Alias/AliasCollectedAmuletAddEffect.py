from Foundation.DemonManager import DemonManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasCollectedAmuletAddEffect(TaskAlias):
    def _onParams(self, params):
        super(AliasCollectedAmuletAddEffect, self)._onParams(params)
        self.Item = params.get("Item")
        pass

    def _onGenerate(self, source):
        Amulet = DemonManager.getDemon("CollectedAmulet")

        Camera = Mengine.getRenderCamera2D()
        P2 = Amulet.calcWorldHintPoint()

        ItemEntity = self.Item.getEntity()
        sprite = ItemEntity.generatePure()
        # size = sprite.getImageSize()

        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2[0], P0[1])

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(sprite)

        sprite.setLocalPosition(P0)

        # scaleToX = InventorySlotSize/size.x
        # scaleToY = InventorySlotSize/size.y

        # scaleTo = min(scaleToX, scaleToY)

        # length = Mengine.length_v2_v2( P1, P2 )

        # SpeedEffectInventoryAddInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000)
        # time = length / SpeedEffectInventoryAddInventoryItem

        # with source.addParallelTask(2) as (tcp0, tcp1):
        #     tcp0.addTask( "TaskNodeBezier2To", Node = sprite, Point1 = P1, To = P2, Speed = 1000)
        #     tcp1.addTask( "TaskNodeScaleTo", Node = sprite, To = (scaleTo, scaleTo, 1.0), Time = time )
        #     pass

        speed = 500
        speed *= 0.001  # speed fix

        source.addTask("TaskNodeBezier2To", Node=sprite, Point1=P1, To=P2, Speed=speed)
        source.addTask("TaskNodeRemoveFromParent", Node=sprite)
        source.addTask("TaskNodeDestroy", Node=sprite)

        pass

    pass
