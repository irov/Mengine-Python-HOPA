from Foundation.ArrowManager import ArrowManager
from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager


class SystemInventoryItemAdd(System):
    def _onParams(self, params):
        super(SystemInventoryItemAdd, self)._onParams(params)

        self.Inventory = DemonManager.getDemon("Inventory")

        self.onInventorySlotSetItemObserver = None

        self.slots = {}
        pass

    def _onRun(self):
        self.addObserver(Notificator.onInventorySlotSetItem, self._onInventorySlotSetItem)
        pass

    def _onStop(self):
        self._cleanSlots()
        pass

    def _cleanSlots(self):
        for slot, movieTuple in self.slots.items():
            TaskManager.cancelTaskChain("InventoryItemTip%s" % slot.slotId)

            item = slot.getItem()
            self.__cleanSlot(slot, item)
            pass
        pass

    def __generateSlot(self, slot):
        tempMovie = self._generateMovie("Movie2_ItemTip", slot.slotId)

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

        self.slots[slot] = (tempMovie, textField)

        return tempMovie, textField
        pass

    def __cleanSlot(self, slot, item):
        movie, textField = self.slots[slot]

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

        del self.slots[slot]
        pass

    def _generateMovie(self, name, id):
        obj = self.Inventory.generateObject(name + str(id), name)

        obj.setPosition((0, 0))

        return obj
        pass

    def _onInventorySlotSetItem(self, slot):
        ItemKey = ItemManager.getInventoryItemKey(slot.item)

        if ItemManager.hasTextID(ItemKey) is False:
            return False
            pass

        if TaskManager.existTaskChain("InventoryItemTip%s" % slot.slotId):
            return False
            pass

        tempMovie, textField = self.__generateSlot(slot)

        def __thisSlot(inventoryObject, leaveSlot):
            if leaveSlot is not slot:
                return False
                pass

            return True
            pass

        item = slot.getItem()

        with TaskManager.createTaskChain(Name="InventoryItemTip%s" % slot.slotId) as tc:
            with tc.addRaceTask(6) as (tc_leave, tc_pick, tc_scroll, tc_deactivate, tc_removed, tc_movie):
                tc_leave.addListener(Notificator.onInventorySlotItemLeave, Filter=__thisSlot)

                tc_pick.addListener(Notificator.onInventoryPickInventoryItem, Filter=__thisSlot)

                tc_scroll.addListener(Notificator.onInventoryCurrentSlotIndex)

                tc_deactivate.addListener(Notificator.onInventoryDeactivate)

                tc_removed.addListener(Notificator.onInventoryRemoveInventoryItem)

                tc_movie.addTask("TaskMovie2Play", Movie2=tempMovie, Wait=True)
                pass

            tc.addFunction(self._onSlotMouseLeave, slot, item)
            pass

        return False
        pass

    def _onSlotMouseLeave(self, slot, item):
        self.__cleanSlot(slot, item)

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

        InventoryItemScale = DefaultManager.getDefaultFloat("InventoryItemScale", 1.0)
        InventoryItem.setScale((InventoryItemScale, InventoryItemScale, 1.0))

        slot.setItem(InventoryItem)
        return
        pass

    pass
