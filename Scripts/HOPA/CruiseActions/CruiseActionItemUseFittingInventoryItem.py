from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObjectTemplate import MixinItem
from HOPA.CruiseAction import CruiseAction


class CruiseActionItemUseFittingInventoryItem(MixinItem, CruiseAction):
    def _onParams(self, params):
        super(CruiseActionItemUseFittingInventoryItem, self)._onParams(params)

        self.Inventory = params.get("Inventory")
        if self.Inventory is None:
            if DemonManager.hasDemon("FittingInventory") is True:
                self.Inventory = DemonManager.getDemon("FittingInventory")

        self.InventoryItem = params["InventoryItem"]

    def _getCruiseObject(self):
        return self.Item

    def _onCheck(self):
        if self.Inventory is None:
            return False

        if self.Inventory.hasInventoryItem(self.InventoryItem) is False:
            return False

        return True

    def _onAction(self, source):
        source.addTask("AliasCruiseControlAction", Object=self.InventoryItem)
        source.addTask("AliasCruiseControlAction", Object=self.Item)
        source.addNotify(Notificator.onCruiseActionEnd, self)
