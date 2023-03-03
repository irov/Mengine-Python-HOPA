from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasPickLabItemEffect(TaskAlias):
    def _onParams(self, params):
        super(AliasPickLabItemEffect, self)._onParams(params)
        self.Item = params.get("Item")

    def _onGenerate(self, source):
        Camera = Mengine.getRenderCamera2D()
        button = GroupManager.getObject("Open_Lab", "Button_Lab")
        ObjectEntity = button.getEntity()
        hotspot = ObjectEntity.getHotSpot()
        P2 = hotspot.getWorldPolygonCenter()

        ItemEntity = self.Item.getEntity()
        sprite = ItemEntity.generatePure()
        size = sprite.getSurfaceSize()

        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2[0], P0[1])

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(sprite)

        sprite.setLocalPosition(P0)

        scaleToX = 75 / size.x
        scaleToY = 75 / size.y

        scaleTo = min(scaleToX, scaleToY)

        time = 2.0
        time *= 1000  # speed fix

        with source.addParallelTask(3) as (tc_1, tc_2, tc_3):
            tc_1.addTask("TaskNodeBezier2To", Node=sprite, Point1=P1, To=P2, Time=time)

            tc_2.addTask("TaskNodeAlphaTo", Node=sprite, From=1.0, To=0.0, Time=time)

            tc_3.addTask("TaskNodeScaleTo", Node=sprite, To=(scaleTo, scaleTo, 1.0), Time=time)

        source.addTask("TaskNodeRemoveFromParent", Node=sprite)
        source.addTask("TaskNodeDestroy", Node=sprite)
