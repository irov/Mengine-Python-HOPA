from Foundation.Object.Object import Object


class ObjectFittingInventory(Object):
    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)

        Type.declareParam("SlotCount")
        Type.declareParam("SlotPoints")
        Type.declareParam("SlotPolygon")
        Type.declareParam("InventoryItems")
        Type.declareParam("Fittings")
        pass

    def _onParams(self, params):
        super(ObjectFittingInventory, self)._onParams(params)

        self.initParam("SlotCount", params)
        self.initParam("SlotPoints", params)
        self.initParam("SlotPolygon", params)

        self.initParam("InventoryItems", params, [])
        self.initParam("Fittings", params, [])
        pass

    def hasInventoryItem(self, InventoryItem):
        InventoryItems = self.getParam("InventoryItems")
        for index, inventoryItem in InventoryItems:
            if InventoryItem == inventoryItem:
                return True
                pass
            pass

        return False
        pass

    def getInventoryItemIndex(self, InventoryItem):
        InventoryItems = self.getParam("InventoryItems")

        for index, inventoryItem in InventoryItems:
            if InventoryItem == inventoryItem:
                return index
                pass
            pass

        Trace.log("Object", 0, "FittingInventory %s not found InventoryItem %s" % (self.name, InventoryItem.name))

        return None
        pass

    def hasFitting(self, InventoryItem):
        Fitting = self.getParam("Fittings")

        for index, fitt in Fitting:
            if fitt == InventoryItem:
                return True
                pass
            pass

        return False
        pass

    def hasFittingIndex(self, index):
        Fitting = self.getParam("Fittings")

        for find_index, fitt in Fitting:
            if find_index == index:
                return True
                pass
            pass

        return False
        pass

    def getFittingIndex(self, InventoryItem):
        Fitting = self.getParam("Fittings")

        for index, fitt in Fitting:
            if fitt == InventoryItem:
                return index
                pass
            pass

        Trace.log("Object", 0, "FittingInventory %s not found Fitting %s" % (self.name, InventoryItem.name))

        return None
        pass

    def addFitting(self, Index, InventoryItem):
        if self.hasFittingIndex(Index) is True:
            Trace.log("Object", 0, "FittingInventory.addFitting: already has fitting index %s" % (Index))
            return
            pass

        if self.hasFitting(InventoryItem) is True:
            Trace.log("Object", 0, "FittingInventory.addFitting: has fitting %s:%s" % (Index, InventoryItem.name))
            return
            pass

        self.appendParam("Fittings", (Index, InventoryItem))
        pass

    def hasInventoryItemIndex(self, index):
        InventoryItems = self.getParam("InventoryItems")

        for find_index, name in InventoryItems:
            if find_index == index:
                return True
                pass
            pass

        return False
        pass

    def removeFitting(self, removeIndex):
        if self.hasFittingIndex(removeIndex) is False:
            Trace.log("Object", 0,
                      "FittingInventory.removeFitting: %s not found fitting index %s" % (self.name, removeIndex))
            return
            pass

        Fittings = self.getParam("Fittings")

        for Index, InventoryItem in Fittings:
            if Index == removeIndex:
                self.delParam("Fittings", (Index, InventoryItem))
                pass
            pass
        pass

    def isEmptyItems(self):
        InventoryItems = self.getParam("InventoryItems")

        ItemCount = len(InventoryItems)

        return ItemCount == 0
        pass

    def addInventoryItem(self, InventoryItem):
        if self.hasInventoryItem(InventoryItem) is True:
            Trace.log("Object", 0, "FittingInventory.addInventoryItem: %s already has item %s" % (self.name, InventoryItem.name))
            return
            pass

        Index = self.getInventoryItemSlotIndex(InventoryItem)

        if Index is None:
            Trace.log("Object", 0, "FittingInventory.addInventoryItem: %s not found fitting %s" % (self.name, InventoryItem.name))
            return
            pass

        self.appendParam("InventoryItems", (Index, InventoryItem))
        pass

    def getInventoryItemSlotIndex(self, InventoryItem):
        if self.hasFitting(InventoryItem) is False:
            return None
            pass

        Index = self.getFittingIndex(InventoryItem)

        if self.hasInventoryItemIndex(Index) is True:
            return None
            pass

        return Index
        pass

    def removeInventoryItem(self, InventoryItem):
        if self.hasInventoryItem(InventoryItem) is False:
            Trace.log("Object", 0, "FittingInventory.removeInventoryItem: %s not found item %s" % (self.name, InventoryItem))
            return
            pass

        InventoryItems = self.getParam("InventoryItems")

        for index, inventoryItem in InventoryItems:
            if inventoryItem == InventoryItem:
                self.delParam("InventoryItems", (index, inventoryItem))
                return
                pass
            pass
        pass

    def clear(self):
        InventoryItems = self.getParam("InventoryItems")

        for index, inventoryItem in InventoryItems:
            inventoryItem.setEnable(False)
            pass

        self.setParam("InventoryItems", [])
        self.setParam("Fittings", [])
        pass

    pass
