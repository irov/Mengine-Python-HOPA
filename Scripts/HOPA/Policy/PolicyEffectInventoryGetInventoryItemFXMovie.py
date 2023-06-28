from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias
from HOPA.ItemManager import ItemManager


class PolicyEffectInventoryGetInventoryItemFXMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyEffectInventoryGetInventoryItemFXMovie, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.ItemName = params.get("ItemName")
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
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)

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
        if len(InvItemFoundItems) <= 1:
            InventoryItem.setEnable(False)
            slot.hotspot.disable()
            pass

        point = slot.getPoint()

        Camera = Mengine.getRenderCamera2D()
        P2 = Mengine.getCameraPosition(Camera, point)

        scene = SceneManager.getCurrentScene()
        layer_InventoryItemEffect = scene.getSlot("InventoryItemEffect")

        InventoryItemEntity = InventoryItem.getEntity()

        layer_InventoryItemEffect.addChild(InventoryItemEntity)

        GroupPopUp = GroupManager.getGroup("ItemPopUp")
        Demon_ItemPopUp = GroupPopUp.getObject("Demon_ItemPopUp")
        Point_Item = Demon_ItemPopUp.getObject("Point_Item")

        Point_ItemEntity = Point_Item.getEntity()
        P0 = Point_ItemEntity.getCameraPosition(Camera)
        P1 = (P2[0], P0[1])

        source.addTask("TaskObjectSetPosition", Object=InventoryItem, Value=P0)
        source.addTask("TaskEnable", Object=InventoryItem, Value=True)

        SpeedEffectInventoryGetInventoryItem = DefaultManager.getDefaultFloat("SpeedEffectInventoryGetInventoryItem", 1000.0)
        SpeedEffectInventoryGetInventoryItem *= 0.001  # speed fix
        source.addTask("TaskNodeBezier2To", Node=InventoryItemEntity, Point1=P1, To=P2, Speed=SpeedEffectInventoryGetInventoryItem)

        source.addTask("TaskNodeRemoveFromParent", Node=InventoryItemEntity)

        def __slotSetItem(slot):
            slot.setItem(InventoryItem)
            pass

        source.addTask("TaskFunction", Fn=__slotSetItem, Args=(slot,))
        source.addTask("TaskNodeEnable", Node=InventoryItemEntity, Value=True)

        source.addTask("TaskScope", Scope=self.__playMovieEnd, Args=(slot,))
        pass

    def __attachMovie(self, movieName, slot):
        movie = self.Inventory.generateObject(movieName + str(slot.slotId), movieName)
        movie.setPosition((0, 0))

        movieEntity = movie.getEntity()

        slotPos = slot.point.getWorldPosition()
        movieNode = movieEntity.getAnimatable()
        movieSize = movieNode.getSize()
        MovieOffset = (-(movieSize.x * 0.5), -(movieSize.y * 0.5))

        movieEntityPos = (slotPos.x + MovieOffset[0], slotPos.y + MovieOffset[1])
        movieEntity.setLocalPosition(movieEntityPos)
        return movie
        pass

    def __playMovieEnd(self, scope, slot):
        InventoryItem = ItemManager.getItemInventoryItem(self.ItemName)
        Movie_ItemAdd = self.__attachMovie("Movie_ItemAdd", slot)

        Movie_ItemAddEntity = Movie_ItemAdd.getEntity()

        textField = Mengine.createNode("TextField")
        slotText = Movie_ItemAddEntity.getMovieSlot("text")
        ItemKey = ItemManager.getInventoryItemKey(slot.item)
        textID = ItemManager.getTextID(ItemKey)
        textField.setTextId(textID)
        slotText.addChild(textField)

        textField.setVerticalCenterAlign()
        textField.setCenterAlign()

        slotItem = Movie_ItemAddEntity.getMovieSlot("item")
        itemEntity = slot.item.getEntity()
        slotItem.addChild(itemEntity)

        def __this(inventoryObject, curItem):
            if curItem == InventoryItem:
                return True
                pass
            return False
            pass

        with scope.addRaceTask(2) as (tc1, tc2):
            tc1.addTask("TaskMoviePlay", Movie=Movie_ItemAdd, Wait=True)
            tc2.addTask("TaskListener", ID=Notificator.onInventorySlotItemEnter, Filter=__this)
            pass

        scope.addTask("TaskFunction", Fn=self.__onPlayMovieEnd, Args=(slot, slot.item, Movie_ItemAdd, textField))

        pass

    def __cleanSlot(self, slot, item, Movie_ItemAdd, textField):
        textField.disable()
        textField.removeFromParent()
        Mengine.destroyNode(textField)

        itemEntity = item.getEntity()
        itemEntity.removeFromParent()

        Movie_ItemAdd.removeFromParent()
        Movie_ItemAdd.onDestroy()

        curr_item = slot.getItem()

        if curr_item is None:
            return
            pass

        if curr_item is not item:
            return
            pass

        slot.setItem(item)
        pass

    def __onPlayMovieEnd(self, slot, item, Movie_ItemAdd, textField):
        self.__cleanSlot(slot, item, Movie_ItemAdd, textField)

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
