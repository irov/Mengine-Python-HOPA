from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias


class TaskEffectInventoryGetInventoryItem(TaskAlias):
    def _onParams(self, params):
        super(TaskEffectInventoryGetInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.InventoryItem = params.get("InventoryItem")
        pass

    def _onCheck(self):
        if self.Inventory.isActive() is False:
            return False
            pass

        InventoryEntity = self.Inventory.getEntity()

        if InventoryEntity.isActivate() is False:
            return False
            pass

        return True
        pass

    def _onGenerate(self, source):
        if self.Inventory.isActive() is False:
            return
            pass

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryEntity = self.Inventory.getEntity()
        slot = InventoryEntity.findSlot(self.InventoryItem)

        if slot is None:
            return False
            pass

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

        source.addNotify(Notificator.onInventoryRise)

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            InventoryItemEntity = self.InventoryItem.getEntity()

            itemSpriteSize = InventoryItemEntity.getSpriteCenter()
            effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            node.addChildFront(effectEntityNode)

            source.addEnable(effect)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        GroupPopUp = GroupManager.getGroup("ItemPopUp")
        Demon_ItemPopUp = GroupPopUp.getObject("Demon_ItemPopUp")
        Point_Item = Demon_ItemPopUp.getObject("Point_Item")
        # Demon_Entity=Demon_ItemPopUp.getEntity()

        Point_ItemEntity = Point_Item.getEntity()
        # item=Demon_Entity.InventoryItem

        Item_Entity = self.InventoryItem.getEntity()
        Center = Item_Entity.getSpriteCenter()

        P0 = Point_ItemEntity.getCameraPosition(Camera)
        P0 = (P0.x - Center.x, P0.y - Center.y)
        P1 = (P2[0], P0[1])

        node.setLocalPosition(P0)

        # source.addTask("TaskObjectSetPosition", Object = self.InventoryItem, Value = P0)
        source.addEnable(self.InventoryItem)

        SpeedEffectInventoryGetInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryGetInventoryItem", 350.0)
        Time = 400.0 * (1000.0 / SpeedEffectInventoryGetInventoryItem)
        SpeedEffectInventoryGetInventoryItem *= 0.001  # speed fix

        # source.addTask("TaskNodeBezier2To", Node = node, Point1 = P1, To = P2, Speed = SpeedEffectInventoryGetInventoryItem)
        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addNotify(Notificator.onSoundEffectOnObject, self.InventoryItem, "MoveItemToInventory")

            # tcp0.addTask("TaskNodeBezier2To", Node=node, Point1=Point1, To=P2, Time=Time)
            tcp0.addTask("TaskNodeBezier2WorldFollow", Follow=node2, Node=node, Time=Time)  # Offset=negative_Offset

            # tcp1.addTask("TaskNodeScaleTo", Node=node, To=(scaleTo, scaleTo, 1.0), Time=Time) #Find me plz

            tcp1.addTask("TaskNodeAlphaTo", Node=node, From=1.0, To=0.0, Time=Time)  # CHeat    need to scale insted

        source.addTask("TaskNodeRemoveFromParent", Node=InventoryItemEntityNode)

        source.addFunction(slot.setItem, self.InventoryItem)

        if effect is not None:
            with source.addFork() as source_fork:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                pass

                source_fork.addTask("TaskNodeDestroy", Node=node)
                source_fork.addTask("TaskNodeDestroy", Node=node2)
            pass

        return False
        pass

    pass
