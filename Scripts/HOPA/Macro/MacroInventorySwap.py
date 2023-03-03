from Foundation.Notificator import Notificator
from Foundation.SystemManager import SystemManager
from HOPA.InventoryPanelManager import InventoryPanelManager
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.System.SystemInventoryPanel import SystemInventoryPanel
from HOPA.ZoomManager import ZoomManager


class MacroInventorySwap(MacroCommand):
    def _onValues(self, values):
        self.InventoryName = values[0]
        self.boolOnZoomRepeat = False

        self.wait = False

        if len(values) > 1:
            self.boolOnZoomRepeat = values[1] == 'onZoomRepeat'
            self.wait = values[1] == 'wait'

    def _onInitialize(self):
        super(MacroInventorySwap, self)._onInitialize()

        if _DEVELOPMENT is True:
            if not InventoryPanelManager.hasInventory(self.InventoryName):
                self.initializeFailed("Macro {} -> Inventory Name: \"{}\" not in InventoryPanelManager".format(self.ID, self.InventoryName))

        if not self.boolOnZoomRepeat:
            return

        if _DEVELOPMENT is True:
            if not ZoomManager.hasZoom(self.GroupName):
                self.initializeFailed("onZoomRepeat is True but group of Macro {} is not zoom".format(self.ID))

    def __checkInventory(self):
        systemInventoryPanel = SystemManager.getSystem("SystemInventoryPanel")
        InventoryName = systemInventoryPanel.getActiveInventoryName()
        if self.InventoryName == InventoryName:
            return False
        return True

    def _onGenerate(self, source):
        with source.addIfTask(self.__checkInventory) as (swap, same_inventory):
            swap.addNotify(Notificator.onInventoryChage, self.InventoryName, self.boolOnZoomRepeat, self.GroupName)
            if self.wait:
                swap.addEvent(SystemInventoryPanel.tc_Inventory_finish_event)

            same_inventory.addDummy()
            if _DEVELOPMENT is True:
                same_inventory.addPrint("<MacroInventorySwap> inventory is already {!r}".format(self.InventoryName))
