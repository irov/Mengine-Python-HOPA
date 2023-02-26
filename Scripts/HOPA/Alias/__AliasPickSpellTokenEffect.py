from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias

class __AliasPickSpellTokenEffect(TaskAlias):
    """
    deprecated
    """

    def _onParams(self, params):
        super(AliasPickSpellTokenEffect, self)._onParams(params)
        self.Item = params.get("Item")
        self.Spell = params.get("Spell")
        pass

    def _onGenerate(self, source):
        Camera = Mengine.getRenderCamera2D()
        ObjectEntity = self.Spell.getEntity()
        Socket = ObjectEntity.getSocket()
        SocketEntity = Socket.getEntity()
        hotspot = SocketEntity.getHotSpot()
        P2 = hotspot.getWorldPolygonCenter()

        ItemEntity = self.Item.getEntity()
        sprite = ItemEntity.generatePure()
        # size = sprite.getImageSize()

        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2[0], P0[1])

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(sprite)

        sprite.setLocalPosition(P0)

        time = 2.0
        time *= 1000  # speed fix

        with source.addParallelTask(2) as (tc_1, tc_2):
            tc_1.addTask("TaskNodeBezier2To", Node=sprite, Point1=P1, To=P2, Time=time)

            tc_2.addTask("TaskNodeAlphaTo", Node=sprite, From=1.0, To=0.0, Time=time)
            pass
        source.addTask("TaskNodeRemoveFromParent", Node=sprite)
        source.addTask("TaskNodeDestroy", Node=sprite)
        pass

    pass