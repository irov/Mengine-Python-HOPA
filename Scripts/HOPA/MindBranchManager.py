from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager
from HOPA.ItemManager import ItemManager


class MindBranchManager(object):
    s_branch = []

    class MindBranch(object):
        def __init__(self, inventory_item, group, socket_name, mindId):
            self.InventoryItemName = inventory_item
            self.GroupName = group
            self.SocketName = socket_name
            self.MindId = mindId
            pass

        def getObserveSocket(self):
            SocketInstance = GroupManager.getObject(self.GroupName, self.SocketName)
            return SocketInstance
            pass

        def getAttachedItem(self):
            ItemInstance = ItemManager.getItemInventoryItem(self.InventoryItemName)
            return ItemInstance
            pass

        def getItemName(self):
            return self.InventoryItemName
            pass

        def getGroupName(self):
            return self.GroupName
            pass

        def getMind(self):
            return self.MindId
            pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            inventory_item = record.get("ItemName")
            group = record.get("Group")
            socket = record.get("Socket")
            mindId = record.get("MindId")
            entire = MindBranchManager.MindBranch(inventory_item, group, socket, mindId)
            MindBranchManager.s_branch.append(entire)  # we dont need mapping

        return True

    @staticmethod
    def gets_all():
        return MindBranchManager.s_branch
