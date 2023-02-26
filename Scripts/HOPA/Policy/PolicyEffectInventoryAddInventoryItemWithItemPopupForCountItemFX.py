from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager

class PolicyEffectInventoryAddInventoryItemWithItemPopupForCountItemFX(TaskAlias):
    def _onParams(self, params):
        super(PolicyEffectInventoryAddInventoryItemWithItemPopupForCountItemFX, self)._onParams(params)

        self.ItemName = params.get("ItemName")
        self.Inventory = params.get("Inventory")
        self.hasInventoryItem = params.get("hasInventoryItem", None)
        pass

    def _onInitialize(self):
        super(PolicyEffectInventoryAddInventoryItemWithItemPopupForCountItemFX, self)._onInitialize()

        self.effect = None
        self.sprite = None
        self.node = None

        self.start_pos = None
        self.end_pos = None
        pass

    def _onCheck(self):
        super(PolicyEffectInventoryAddInventoryItemWithItemPopupForCountItemFX, self)._onCheck()
        if self.Inventory.isActive() is False:
            return False
            pass

        scene = SceneManager.getCurrentScene()
        if scene is None:
            return False
            pass

        InventoryEntity = self.Inventory.getEntity()
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        slot = InventoryEntity.findSlot(InventoryItem)

        if slot is None:
            msg = "{ClassName}: invalid find slot for inventory item {Name}:{Object}".format(ClassName=self.__name__, Name=self.ItemName, Object=InventoryItem)
            Trace.log("Policy", 0, msg)
            return False
            pass

        return True
        pass

    def _start_effect_scope(self, source):
        if self.effect is None:
            return

        effectEntityNode = self.effect.getEntityNode()

        itemSpriteSize = self.sprite.getLocalImageCenter()
        effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

        self.node.addChildFront(effectEntityNode)

        source.addTask("TaskEnable", Object=self.effect, Value=True)
        source.addTask("TaskMovie2Play", Movie2=self.effect, Wait=False)
        pass

    def _setup(self):
        # def service vars
        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")

        Item = ItemManager.getItemObject(self.ItemName)
        ItemEntity = Item.getEntity()
        Camera = Mengine.getRenderCamera2D()

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        # calc start pos
        self.start_pos = ItemEntity.getCameraPosition(Camera)

        # setup effect
        self.effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        # setup node
        self.node = Mengine.createNode("Interender")
        layer_InventoryItemEffect.addChild(self.node)

        self.node.setLocalPosition(self.start_pos)

        # setup sprite
        self.sprite = ItemEntity.generatePure()

        spriteCenter = self.sprite.getLocalImageCenter()
        self.sprite.coordinate(spriteCenter)

        self.node.addChild(self.sprite)

        # calc end pos
        bb = self.sprite.getBoundingBox()
        sprite_w, sprite_h = bb.maximum.x - bb.minimum.x, bb.maximum.y - bb.minimum.y

        offset_x, offset_y = sprite_w / 2, sprite_h / 2

        Demon = GroupManager.getObject("ItemPopUp", "Demon_ItemPopUp")
        Point = Demon.getObject("Point_Item")

        pos_x, pos_y = Point.getPosition()

        imageSize = self.sprite.getSurfaceSize()

        scaleToX = InventorySlotSize / imageSize.x
        scaleToY = InventorySlotSize / imageSize.y
        scaleTo = min(scaleToX, scaleToY)

        self.end_pos = (pos_x - offset_x * scaleTo, pos_y - offset_y * scaleTo)
        pass

    def _scale_scope(self, source):
        source.addTask("TaskNodeScaleTo", Node=self.sprite, To=(1.25, 1.25, 1.0), Time=250.0)
        source.addTask("TaskNodeScaleTo", Node=self.sprite, To=(1.0, 1.0, 1.0), Time=250.0)
        pass

    def _clean_scope(self, source):
        with source.addFork() as source_fork:
            if self.effect is not None:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=self.effect)
                source_fork.addTask("TaskObjectDestroy", Object=self.effect)
                pass

            source_fork.addTask("TaskNodeDestroy", Node=self.node)
            pass
        pass

    def _move_to_center_scope(self, source):
        # def vars
        Item = ItemManager.getItemObject(self.ItemName)
        imageSize = self.sprite.getSurfaceSize()
        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        # calc scale to
        scaleToX = InventorySlotSize / imageSize.x
        scaleToY = InventorySlotSize / imageSize.y
        scaleTo = min(scaleToX, scaleToY)

        # calc time
        length = Mengine.length_v2_v2(self.start_pos, self.end_pos)
        SpeedEffectInventoryAddInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000.0)
        SpeedEffectInventoryAddInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectInventoryAddInventoryItem

        # task chain
        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addNotify(Notificator.onSoundEffectOnObject, Item, "MoveItemToInventory")
            tcp0.addTask("TaskNodeBezier2To", Node=self.node, Point1=self.start_pos, To=self.end_pos, Speed=SpeedEffectInventoryAddInventoryItem)

            tcp1.addTask("TaskNodeScaleTo", Node=self.node, To=(scaleTo, scaleTo, 1.0), Time=time)
            pass
        pass

    def _get_item_scope(self, source):
        with source.addParallelTask(2) as (source_pop_up, source_alpha):
            source_pop_up.addTask("AliasInventoryItemPopUp", ItemName=self.ItemName, Inventory=self.Inventory)

            source_alpha.addDelay(200.0)
            source_alpha.addTask("TaskNodeAlphaTo", Node=self.sprite, From=1.0, To=0.0, Time=250.0)
            source_alpha.addTask("TaskNodeEnable", Node=self.sprite, Value=False)
            pass
        pass

    def _add_inventory_item(self, scope, itemName):
        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        InventoryItems = self.Inventory.getParam("InventoryItems")
        SlotCount = self.Inventory.getParam("SlotCount")

        InventoryItem = ItemManager.getItemInventoryItem(itemName)

        if self.Inventory.hasInventoryItem(InventoryItem) is False:
            InventoryItemIndex = len(InventoryItems)
        else:
            InventoryItemIndex = self.Inventory.indexInventoryItem(InventoryItem)
            pass

        NewSlotIndex = int(InventoryItemIndex / SlotCount) * SlotCount

        if CurrentSlotIndex != NewSlotIndex:
            with GuardBlockInput(scope) as guard_source:
                guard_source.addTask("TaskInventorySlotsHideInventoryItem", Inventory=self.Inventory)
                guard_source.addTask("TaskInventoryCurrentSlotIndex", Inventory=self.Inventory, Value=NewSlotIndex)
                guard_source.addTask("TaskInventorySlotsShowInventoryItem", Inventory=self.Inventory)
                pass
            pass

        with scope.addParallelTask(2) as (scope_fade_out, scope_get_item):
            scope_fade_out.addTask("AliasFadeOut", FadeGroupName="FadeDialog", From=0.3, Time=0.2 * 1000, Unblock=True)  # speed fix

            scope_get_item.addTask("TaskInventoryAddItem", Inventory=self.Inventory, ItemName=itemName)
            scope_get_item.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.Inventory, InventoryItem=InventoryItem)

            # todo: implement this as task
            scope_get_item.addScope(self._get_to_inventory)

        if Mengine.hasResource("ItemToSlot") is True:
            scope.addTask("TaskSoundEffect", SoundName="ItemToSlot", Wait=False)
            pass
        pass

    def _get_to_inventory(self, source):
        if self.Inventory.isActive() is False:
            return
            pass

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryEntity = self.Inventory.getEntity()

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        slot = InventoryEntity.findSlot(InventoryItem)

        if slot is None:
            return False
            pass

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        InventoryItemEntity = InventoryItem.getEntity()
        InventoryItemSpriteCenter = InventoryItemEntity.getSpriteCenter()

        P2.x = P2.x + InventoryItemSpriteCenter.x
        P2.y = P2.y + InventoryItemSpriteCenter.y

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")

        node = Mengine.createNode("Interender")

        layer_InventoryItemEffect.addChild(node)

        self.sprite.setLocalPosition((0.0, 0.0))

        node.addChild(self.sprite)

        if effect is not None:
            effectEntityNode = effect.getEntityNode()

            itemSpriteSize = self.sprite.getSpriteCenter()

            effectEntityNode.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            node.addChildFront(effectEntityNode)

            source.addTask("TaskEnable", Object=effect, Value=True)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        GroupPopUp = GroupManager.getGroup("ItemPopUp")
        Demon_ItemPopUp = GroupPopUp.getObject("Demon_ItemPopUp")
        Point_Item = Demon_ItemPopUp.getObject("Point_Item")

        Point_ItemEntity = Point_Item.getEntity()
        P0 = Point_ItemEntity.getCameraPosition(Camera)
        P1 = (P2[0], P0[1])

        node.setLocalPosition(P0)

        source.addTask("TaskNodeEnable", Node=self.sprite, Value=True)
        source.addTask("TaskNodeAlphaTo", Node=self.sprite, From=0.0, To=1.0, Time=1)

        SpeedEffectInventoryGetInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryGetInventoryItem", 1000.0)
        SpeedEffectInventoryGetInventoryItem *= 0.001  # speed fix

        positionFrom = node.getLocalPosition()
        length = Mengine.length_v2_v2(positionFrom, P2)
        Time = length / SpeedEffectInventoryGetInventoryItem

        with source.addParallelTask(2) as (source_move, source_scale):
            source_move.addTask("TaskNodeBezier2To", Node=node, Point1=P1, To=P2, Speed=SpeedEffectInventoryGetInventoryItem)

            source_scale.addTask("TaskNodeScaleTo", Node=self.sprite, To=(0.5, 0.5, 1.0), Time=Time)

        source.addTask("TaskNodeAlphaTo", Node=self.sprite, From=1.0, To=0.0, Time=250.0)
        source.addTask("TaskNodeEnable", Node=self.sprite, Value=False)

        if effect is not None:
            with source.addFork() as source_fork:
                source_fork.addTask("TaskMovie2Interrupt", Movie2=effect)
                source_fork.addTask("TaskObjectDestroy", Object=effect)
                pass

                source_fork.addTask("TaskNodeDestroy", Node=node)
            pass
        pass

    def _inv_item_submovie(self, source):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        InventoryItemEntity = InventoryItem.getEntity()

        source.addTask("TaskEnable", Object=InventoryItem, Value=True)

        source.addFunction(InventoryItemEntity.playSubMovie, self.ItemName)
        pass

    def _onGenerate(self, source):
        self._setup()

        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        FoundItems = InventoryItem.getParam("FoundItems")
        if len(FoundItems) > 1:
            source.addTask("TaskEnable", Object=InventoryItem, Value=True)

        source.addScope(self._scale_scope)

        source.addScope(self._start_effect_scope)

        source.addScope(self._move_to_center_scope)

        source.addScope(self._get_item_scope)

        source.addScope(self._add_inventory_item, self.ItemName)

        source.addScope(self._inv_item_submovie)

        source.addScope(self._clean_scope)
        pass
    pass