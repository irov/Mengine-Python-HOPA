from Foundation.PolicyManager import PolicyManager
from HOPA.CruiseAction import CruiseAction


class CruiseActionCombine(CruiseAction):
    def __init__(self):
        super(CruiseActionCombine, self).__init__()
        pass

    def _onParams(self, params):
        super(CruiseActionCombine, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        self.AttachInventoryItem = params.get("AttachInventoryItem")
        self.SlotInventoryItem = params.get("SlotInventoryItem")
        pass

    def _onCheck(self):
        if self.Inventory.hasInventoryItem(self.AttachInventoryItem) is False:
            return False
            pass

        if self.Inventory.hasInventoryItem(self.SlotInventoryItem) is False:
            return False
            pass

        return True
        pass

    def _onAction(self, source):
        PolicyInventoryScrolling = PolicyManager.getPolicy("InventoryScrolling")
        source.addTask(PolicyInventoryScrolling, InventoryItem=self.AttachInventoryItem)
        source.addTask("AliasCruiseControlAction", Object=self.AttachInventoryItem)
        source.addTask(PolicyInventoryScrolling, InventoryItem=self.SlotInventoryItem)
        source.addTask("AliasCruiseControlAction", Object=self.SlotInventoryItem)
        source.addNotify(Notificator.onCruiseActionEnd, self)
