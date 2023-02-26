from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class InventoryPanelManager(Manager):
    s_data = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            InventoryName = record.get("InventoryName")

            InventoryPanelManager.s_data[InventoryName] = InventoryName

        return True

    @staticmethod
    def hasInventory(inv_name):
        return inv_name in InventoryPanelManager.s_data

    @staticmethod
    def getData():
        return InventoryPanelManager.s_data