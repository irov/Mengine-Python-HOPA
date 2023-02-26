from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class HOGFittingInventoryManager(object):
    s_objects = {}

    @staticmethod
    def onFinalize():
        HOGFittingItemManager.s_items = {}
        pass

    @staticmethod
    def loadInventoryData(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            HOGName = record.get("HOGName")
            InvGroupName = record.get("GroupName")
            InvObjName = record.get("ObjectName")

            Inventory = None
            if GroupManager.hasObject(InvGroupName, InvObjName) is True:
                Inventory = GroupManager.getObject(InvGroupName, InvObjName)
                pass

            HOGFittingInventoryManager.s_objects[HOGName] = Inventory
            pass
        pass

    @staticmethod
    def getInventory(name):
        if HOGFittingInventoryManager.hasInventory(name) is False:
            return None
            pass
        Inventory = HOGFittingInventoryManager.s_objects[name]
        return Inventory
        pass

    @staticmethod
    def hasInventory(name):
        if name not in HOGFittingInventoryManager.s_objects:
            return False
            pass
        return True
        pass
    pass