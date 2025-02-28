from Foundation.DefaultManager import DefaultManager
from Foundation.Object.ObjectPoint import ObjectPoint
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias


class TaskEffectInventoryAddInventoryItemFromPoint(TaskAlias):
    def _onParams(self, params):
        super(TaskEffectInventoryAddInventoryItemFromPoint, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.InventoryItem = params.get("InventoryItem")
        self.FromPoint = params.get("FromPoint")

    def _onCheck(self):
        if self.Inventory.isActive() is False:
            return False

        InventoryEntity = self.Inventory.getEntity()

        if InventoryEntity.isActivate() is False:
            return False

        return True

    def _onGenerate(self, source):
        if self.Inventory.isActive() is False:
            return

        if self.InventoryItem is None:
            msg = "Inventory Item is None"
            self.log(msg)

        if self.InventoryItem.isActive() is False:
            msg = "Inventory Item {} is not active"
            msg = msg.format(self.InventoryItem.name)
            self.log(msg)

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryEntity = self.Inventory.getEntity()
        slot = InventoryEntity.findSlot(self.InventoryItem)

        if slot is None:
            msg = "inventory {} can't find slot for {}"
            msg = msg.format(self.Inventory.name, self.InventoryItem.name)
            self.log(msg)
            return False

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")

        node = Mengine.createNode("Interender")
        node2 = Mengine.createNode("Interender")

        InventoryNode = self.Inventory.getEntityNode()
        InventoryNode.addChild(node2)
        node2.setWorldPosition(P2)

        layer_InventoryItemEffect.addChild(node)

        InventoryItemEntityNode = self.InventoryItem.getEntityNode()
        InventoryItemEntityNode.setLocalPosition((0.0, 0.0))
        node.addChild(InventoryItemEntityNode)

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            InventoryItemEntity = self.InventoryItem.getEntity()

            itemSpriteSize = InventoryItemEntity.getSpriteCenter()
            effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            node.addChildFront(effectEntityNode)

            source.addEnable(effect)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)

        # handle self.FromPoint
        if isinstance(self.FromPoint, tuple):
            P0 = Mengine.vec3f(self.FromPoint[0], self.FromPoint[1], 0.0)

        elif isinstance(self.FromPoint, ObjectPoint):
            FromPointEntity = self.FromPoint.getEntity()
            P0 = FromPointEntity.getCameraPosition(Camera)

        else:
            msg = "FromPoint is invalid, set to (0.0, 0.0). FromPoint should be ObjectPoint or tuple(x, y)"
            self.log(msg)
            P0 = Mengine.vec3f(0.0, 0.0, 0.0)

        P1 = (P2[0], P0[1])

        node.setLocalPosition(P0)

        source.addEnable(self.InventoryItem)

        SpeedEffectInventoryGetInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000.0)
        Time = 400.0 * (1000.0 / SpeedEffectInventoryGetInventoryItem)
        SpeedEffectInventoryGetInventoryItem *= 0.001  # speed fix

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addNotify(Notificator.onSoundEffectOnObject, self.InventoryItem, "MoveItemToInventory")
            tcp0.addTask("TaskNodeBezier2WorldFollow", Follow=node2, Node=node, Time=Time)  # Offset=negative_Offset

            tcp1.addTask("TaskNodeAlphaTo", Node=node, From=1.0, To=0.0, Time=Time)  # CHeat    need to scale insted

        source.addTask("TaskNodeRemoveFromParent", Node=InventoryItemEntityNode)

        source.addFunction(slot.setItem, self.InventoryItem)

        if effect is not None:
            with source.addFork() as source_fork:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                source_fork.addTask("TaskNodeDestroy", Node=node)
        return False
