from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.HOGManager import HOGManager


class AliasHOGRollingItemFoundEffect(TaskAlias):
    def _onParams(self, params):
        super(AliasHOGRollingItemFoundEffect, self)._onParams(params)
        self.HOGItemName = params.get("HOGItemName")
        self.HOG = params.get("HOG")
        self.EnigmaName = params.get("EnigmaName")
        pass

    def _onGenerate(self, source):
        HOGInventory = HOGManager.getInventory(self.EnigmaName)

        if HOGInventory.isActive() is False:
            return
            pass

        effect = HOGInventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        hogItem = HOGManager.getHOGItem(self.EnigmaName, self.HOGItemName)
        self.ItemName = hogItem.objectName

        InventoryEntity = HOGInventory.getEntity()
        slot = InventoryEntity.getSlotByName(self.HOGItemName)

        if slot is None:
            self.invalidTask("not found slot %s" % (self.HOGItemName))
            pass

        P2 = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()

        Item = self.Group.getObject(self.ItemName)
        Item.setBlock(False)
        ItemEntity = Item.getEntity()

        node = Mengine.createNode("Interender")

        pure = ItemEntity.generatePure()
        pure.enable()

        pureCenter = pure.getLocalImageCenter()
        pureWorldCenter = pure.getWorldImageCenter()
        itemPosition = ItemEntity.getCameraPosition(Camera)
        P0 = (itemPosition[0] + pureWorldCenter.x, itemPosition[1] + pureWorldCenter.y)

        P1 = (P2.x, P0[1])

        scene = SceneManager.getCurrentScene()
        if Mengine.hasTouchpad() is True:
            layer = scene.getMainLayer()
        else:
            layer = scene.getSlot("HOGViewport")
        layer.addChild(node)

        node.addChild(pure)
        node.setLocalPosition(P0)
        pure.setLocalPosition((0.0, 0.0))
        pure.setOrigin(pureCenter)

        HOGItemHideEffectSpeed = DefaultManager.getDefaultFloat("HOGItemHideEffectSpeed", 1000)
        HOGItemHideEffectSpeed *= 0.001  # speed fix
        HOGItemIncreaseTime = DefaultManager.getDefaultFloat("HOGItemIncreaseTime", 1)
        HOGItemIncreaseTime *= 1000  # speed fix

        length = Mengine.length_bezier2(P0, P1, P2)
        time = length / HOGItemHideEffectSpeed
        # time *= 1000  # speed fix
        disappearTime = max(time * 0.1, 200.0)
        disappearDelay = max(time - disappearTime * 0.5, 0.0)

        source.addTask("TaskNodeScaleTo", Node=pure, To=(1.5, 1.5, 1.0), Time=HOGItemIncreaseTime)

        if effect is not None:
            effectEntityNode = effect.getEntityNode()
            effectEntityNode.setLocalPosition((0.0, 0.0))

            node.addChildFront(effectEntityNode)

            source.addEnable(effect)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        with source.addParallelTask(3) as (tcp0, tcp1, tcp2):
            tcp0.addTask("TaskNodeBezier2To", Node=node, Point1=P1, To=P2, Time=time)

            tcp1.addDelay(disappearDelay)
            tcp1.addTask("TaskNodeScaleTo", Node=node, To=(0.0, 0.0, 1.0), Time=disappearTime, Easing="easyCubicInOut")

            tcp2.addDelay(disappearDelay)
            tcp2.addTask("TaskNodeAlphaTo", Node=node, From=1.0, To=0.0, Time=disappearTime, Easing="easyCubicInOut")
            pass

        source.addTask("TaskNodeEnable", Node=pure, Value=False)

        with source.addFork() as source_fork:
            if effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=node)
            pass
