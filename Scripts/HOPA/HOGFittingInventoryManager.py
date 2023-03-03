from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class HOGFittingInventoryManager(object):
    s_objects = {}

    @staticmethod
    def onFinalize():
        HOGFittingInventoryManager.s_objects = {}

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

            HOGFittingInventoryManager.s_objects[HOGName] = Inventory

    @staticmethod
    def getInventory(name):
        if HOGFittingInventoryManager.hasInventory(name) is False:
            return None
        Inventory = HOGFittingInventoryManager.s_objects[name]
        return Inventory

    @staticmethod
    def hasInventory(name):
        if name not in HOGFittingInventoryManager.s_objects:
            return False
        return True
