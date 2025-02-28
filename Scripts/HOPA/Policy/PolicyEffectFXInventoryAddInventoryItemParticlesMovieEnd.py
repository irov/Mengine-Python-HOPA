from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class PolicyEffectFXInventoryAddInventoryItemParticlesMovieEnd(TaskAlias):
    def _onParams(self, params):
        super(PolicyEffectFXInventoryAddInventoryItemParticlesMovieEnd, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        self.Inventory = params.get("Inventory")
        pass

    def _onGenerate(self, source):
        if self.Inventory.isActive() is False:
            return
            pass

        effect = self.Inventory.tryGenerateObjectUnique("Effect", "Movie2_ItemTips")

        InventoryEntity = self.Inventory.getEntity()
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

        CountRight = self.Inventory.getScrollCountRight(InventoryItem)
        CountLeft = self.Inventory.getScrollCountLeft(InventoryItem)
        if CountRight >= 1:
            slot = InventoryEntity.getSlot(0)
            pass
        elif CountLeft >= 1:
            lastIndex = DefaultManager.getDefaultInt("InventorySlotCount", 7) - 1
            slot = InventoryEntity.getSlot(lastIndex)
            pass
        else:
            slot = InventoryEntity.findSlot(InventoryItem)
            pass

        InvItemFoundItems = InventoryItem.getFoundItems()
        # print "InvItemFoundItems", InvItemFoundItems
        if len(InvItemFoundItems) <= 1:
            InventoryItem.setEnable(False)
            slot.hotspot.disable()
            pass

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        Item = ItemManager.getItemObject(self.ItemName)
        ItemEntity = Item.getEntity()
        sprite = ItemEntity.getSprite()
        pure = ItemEntity.generatePure()
        pure.disable()

        size = sprite.getSurfaceSize()

        P0 = ItemEntity.getCameraPosition(Camera)

        P1 = (P2.x, P0.y)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")
        layer_InventoryItemEffect.addChild(pure)

        pure.setLocalPosition(P0)

        InventorySlotSize = DefaultManager.getDefaultFloat("InventorySlotSize", 70)

        scaleToX = InventorySlotSize / size.x
        scaleToY = InventorySlotSize / size.y

        scaleTo = min(scaleToX, scaleToY)

        length = Mengine.length_v2_v2(P1, P2)

        SpeedEffectInventoryAddInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryAddInventoryItem", 1000.0)
        SpeedEffectInventoryAddInventoryItem *= 0.001  # speed fix
        time = length / SpeedEffectInventoryAddInventoryItem
        # time *= 1000  # speed fix

        if effect is not None:
            effectEntity = effect.getEntity()

            itemSpriteSize = pure.getLocalImageCenter()

            pure.addChildFront(effectEntity)

            effectEntity.setLocalPosition((itemSpriteSize.x, itemSpriteSize.y))

            source.addEnable(effect)
            source.addTask("TaskMovie2Play", Movie2=effect, Wait=False)
            pass

        source.addTask("TaskNodeEnable", Node=pure, Value=True)

        with source.addParallelTask(2) as (tcp0, tcp1):
            tcp0.addTask("TaskNodeBezier2To", Node=pure, Point1=P1, To=P2, Speed=SpeedEffectInventoryAddInventoryItem)
            tcp1.addTask("TaskNodeScaleTo", Node=pure, To=(scaleTo, scaleTo, 1.0), Time=time)
            pass

        if len(InvItemFoundItems) == 1:
            source.addEnable(InventoryItem)
            source.addTask("TaskNodeEnable", Node=slot.hotspot, Value=True)
            pass

        if effect is not None:
            effectEntity = effect.getEntity()

            source.addTask("TaskMovie2Stop", Movie2=effect)
            source.addTask("TaskNodeRemoveFromParent", Node=effectEntity)
            pass

        source.addTask("TaskNodeRemoveFromParent", Node=pure)

        source.addTask("TaskNodeDestroy", Node=pure)

        source.addScope(self.__playMovieEnd, slot)
        pass

    def __playMovieEnd(self, scope, slot):
        tempMovie = self.Inventory.generateObject("Movie2_ItemTip" + str(slot.slotId), "Movie2_ItemTip")
        tempMovie.setPosition((0, 0))

        movieEntity = tempMovie.getEntity()
        slot.point.addChild(movieEntity)
        movieEntity.setLocalPosition((-100, -100))

        textField = Mengine.createNode("TextField")
        slotText = movieEntity.getMovieSlot("text")
        ItemKey = ItemManager.getInventoryItemKey(slot.item)
        textID = ItemManager.getTextID(ItemKey)
        textField.setTextId(textID)
        slotText.addChild(textField)

        textField.setVerticalCenterAlign()
        textField.setCenterAlign()

        if movieEntity.hasMovieSlot("item") is True:
            slotItem = movieEntity.getMovieSlot("item")
            itemEntity = slot.item.getEntity()
            slotItem.addChild(itemEntity)
            pass

        scope.addTask("TaskMovie2Play", Movie2=tempMovie, Wait=True)
        scope.addScope(self.__onPlayMovieEnd, slot, slot.item, tempMovie, textField)

        pass

    def __cleanSlot(self, slot, item, movie, textField):
        textField.disable()
        textField.removeFromParent()
        Mengine.destroyNode(textField)

        movieEntity = movie.getEntity()

        if movieEntity.hasMovieSlot("item") is True:
            itemEntity = item.getEntity()
            itemEntity.removeFromParent()

            movie.removeFromParent()
            movie.onDestroy()

            curr_item = slot.getItem()

            if curr_item is None:
                return
                pass

            if curr_item is not item:
                return
                pass

            slot.setItem(item)
            pass
        else:
            movie.removeFromParent()
            movie.onDestroy()
            pass
        pass

    def __onPlayMovieEnd(self, slot, item, tempMovie, textField):
        self.__cleanSlot(slot, item, tempMovie, textField)

        CurrentSlotIndex = self.Inventory.getParam("CurrentSlotIndex")
        inventoryItems = self.Inventory.getParam("InventoryItems")

        index = CurrentSlotIndex + slot.slotId

        if len(inventoryItems) <= index:
            return
            pass

        InventoryItem = inventoryItems[index]

        cursorItem = ArrowManager.getArrowAttach()
        if cursorItem == InventoryItem:
            return
            pass

        slotItem = slot.getCursorItem()

        if slotItem is not InventoryItem:
            return
            pass

        InventoryItem.setPosition((0, 0))

        slot.setItem(InventoryItem)
        return
        pass

    pass
