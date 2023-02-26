from Foundation.DemonManager import DemonManager
from HOPA.ItemManager import ItemManager

class FittingInventoryManager(object):
    s_slots = {}

    class Slot(object):
        def __init__(self, index):
            self.index = index
            pass

        def getIndex(self):
            return self.index
            pass
        pass

    @staticmethod
    def loadFittingItems(param):
        FittingItems_Param = param  # Mengine.getParam(param)

        if FittingItems_Param is None:
            Trace.log("Manager", 0, "FittingInventoryManager.loadParam: invalid param %s" % (param))
            return

        for values in FittingItems_Param:
            itemName = values  # values[0].strip()
            #
            #            if itemName == "":
            #                continue
            #
            #            index = int(values[1].strip()) if values[1].strip() != "" else None
            #            slotIndex = index-1
            #            enable = bool(int(values[2].strip()))
            enable = False
            slotIndex = 0
            FittingInventoryManager.addFitting(itemName, slotIndex, enable)
            pass
        pass

    @staticmethod
    def addFitting(itemName, index, enable):
        if itemName in FittingInventoryManager.s_slots:
            Trace.log("Manager", 0, "FittingInventoryManager addFitting: item %s already exist" % (itemName))
            return
            pass

        slot = FittingInventoryManager.Slot(index)

        FittingInventoryManager.s_slots[itemName] = slot

        if itemName is not None:
            InventoryItem = ItemManager.getItemInventoryItem(itemName)

            if InventoryItem is None:
                Trace.log("Manager", 0, "FittingInventoryManager addItem: Cann't get item '%s'" % (itemName))
                return
                pass

            elif enable == True:
                FittingInventory = DemonManager.getDemon("FittingInventory")
                FittingInventory.addFitting(index, InventoryItem)
                pass
            pass
        pass