from Foundation.DefaultManager import DefaultManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager


class SystemInventoryItemText(System):
    def _onParams(self, params):
        super(SystemInventoryItemText, self)._onParams(params)

        self.Inventory = None

        self.slots = {}
        self.InventoryTypes = params.get("InventoryTypes", ["ObjectInventoryFX", "ObjectInventory", "ObjectHOGInventoryFitting"])
        pass

    def _onRun(self):
        self.addObserver(Notificator.onInventorySlotItemEnter, self.__onSlotMouseEnterFilter)

        return True
        pass

    def _onStop(self):
        self._cleanSlots()
        pass

    def _cleanSlots(self):
        for itemKey, movieTuple in self.slots.items():
            TaskManager.cancelTaskChain("InventoryItemTip%s" % slot.slotId)

            InventoryItem = self.Inventory.getInventoryItem(ItemKey)
            self.__cleanSlot(itemKey, InventoryItem)
            pass

        self.slots = {}
        pass

    def __generateSlot(self, ItemKey):
        if ItemKey is None:
            Trace.log("System", 0, "SystemInventoryItemText:__generateSlotItemKey ItemKey is None ")
            return None, None
            pass

        textID = self.Inventory.getItemTextID(ItemKey)
        if textID is None:
            Trace.log("System", 0, "ItemKey %s has not TextID, need add to xlsx " % (ItemKey))
            # print "ItemKey %s has not TextID, need add to xlsx "%(ItemKey)
            return None, None
            pass

        tempMovie = self._generateMovie("Movie2_ItemTip", ItemKey)

        movieEntity = tempMovie.getEntity()

        InventoryItem = self.Inventory.getInventoryItem(ItemKey)

        self.Inventory.attachItemSlotMovie(ItemKey, tempMovie)

        textField = Mengine.createNode("TextField")
        slotText = movieEntity.getMovieSlot("text")

        textField.setTextId(textID)
        slotText.addChild(textField)

        textField.setVerticalCenterAlign()
        textField.setHorizontalCenterAlign()

        if InventoryItem.getEnable() is True:
            if movieEntity.hasMovieSlot("item") is True:
                slotItem = movieEntity.getMovieSlot("item")
                itemEntityNode = InventoryItem.getEntityNode()
                slotItem.addChild(itemEntityNode)
                pass
            pass

        self.slots[ItemKey] = (tempMovie, textField)

        return tempMovie, textField
        pass

    def __cleanSlot(self, itemKey, item):
        movie, textField = self.slots[itemKey]

        textField.disable()
        textField.removeFromParent()
        Mengine.destroyNode(textField)

        InventoryItem = self.Inventory.getInventoryItem(itemKey)

        movieEntity = movie.getEntity()

        if movieEntity.hasMovieSlot("item") is True:
            InventoryItem.returnToParent()
            movie.onDestroy()
            pass
        else:
            movie.onDestroy()
            pass

        del self.slots[itemKey]
        pass

    def _generateMovie(self, name, itemKey):
        obj = self.Inventory.generateObject(name + itemKey, name)

        obj.setPosition((0, 0))

        return obj
        pass

    def __onSlotMouseEnterFilter(self, inventoryObject, item):
        if inventoryObject is None:
            return False
            pass

        if inventoryObject.getType() not in self.InventoryTypes:
            return False
            pass

        self.Inventory = inventoryObject

        ItemKey = self.Inventory.getInventoryItemKey(item)

        if TaskManager.existTaskChain("InventoryItemTip%s" % ItemKey):
            return False
            pass

        tempMovie, textField = self.__generateSlot(ItemKey)

        def __thisSlot(inventoryObject, leaveItem):
            if leaveItem is not item:
                return False
                pass

            return True
            pass

        def __thisPickSlot(leaveItem):
            if leaveItem is not item:
                return False
                pass

            return True
            pass

        InventoryItemTextLoop = DefaultManager.getDefaultBool("InventoryItemTextLoop", True)
        # InventoryItemTextLoop = DefaultManager.getDefaultBool("InventoryItemTextLoop", False)

        with TaskManager.createTaskChain(Name="InventoryItemTip%s" % ItemKey) as tc:
            if InventoryItemTextLoop is True:
                tc.addTask("TaskMovie2Play", Movie2=tempMovie, Loop=True, Wait=False)

                with tc.addRaceTask(5) as (tc_leave, tc_pick, tc_scroll, tc_deactivate, tc_removed):
                    tc_leave.addListener(Notificator.onInventorySlotItemLeave, Filter=__thisSlot)

                    tc_pick.addListener(Notificator.onInventoryPickInventoryItem, Filter=__thisPickSlot)

                    tc_scroll.addListener(Notificator.onInventoryCurrentSlotIndex)

                    tc_deactivate.addListener(Notificator.onInventoryDeactivate)

                    tc_removed.addListener(Notificator.onInventoryRemoveInventoryItem, Filter=__thisSlot)
                    pass
                pass
            else:
                with tc.addRaceTask(6) as (tc_leave, tc_pick, tc_scroll, tc_deactivate, tc_removed, tc_movie):
                    tc_leave.addListener(Notificator.onInventorySlotItemLeave, Filter=__thisSlot)

                    tc_pick.addListener(Notificator.onInventoryPickInventoryItem, Filter=__thisPickSlot)

                    tc_scroll.addListener(Notificator.onInventoryCurrentSlotIndex)

                    tc_deactivate.addListener(Notificator.onInventoryDeactivate)

                    tc_removed.addListener(Notificator.onInventoryRemoveInventoryItem, Filter=__thisSlot)

                    tc_movie.addTask("TaskMovie2Play", Movie2=tempMovie, Loop=False, Wait=True)
                    pass
                pass

            tc.addFunction(self._onSlotMouseLeave, ItemKey, item)
            pass

        return False
        pass

    def _onSlotMouseLeave(self, ItemKey, item):
        self.__cleanSlot(ItemKey, item)
        self.Inventory.returnItemSlot(ItemKey)
        return
        pass

    pass
