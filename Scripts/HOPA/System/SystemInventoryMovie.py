from Foundation.DemonManager import DemonManager
from Foundation.StateManager import StateManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager


class SystemInventoryMovie(System):
    def _onParams(self, params):
        super(SystemInventoryMovie, self)._onParams(params)

        self.Inventory = DemonManager.getDemon("Inventory")
        self.EnableScrolling = True
        self.prepare = False

        self.inventoryState = "INVENTORY_UP"

        self.listChain = [
            "INVENTORY_UP",
            "INVENTORY_LEFT",
            "INVENTORY_RIGHT",
            "INVENTORY_ADDITEM",
            "INVENTORY_ARROWITEM",
            "INVENTORY_RETURNITEM",
            "INVENTORY_REMOVEITEM",
            "INVENTORY_MOVEADDITEM"
        ]

        self.listChain2 = [
            "InventoryPopUpPrepare",
            "InventoryUpPrepare",
            "InventoryDownPrepare",
            "INVENTORY_PrepareTOITEM"
        ]

    def _onRun(self):
        self.addObserver(Notificator.onStateChange, self._onStateChange)
        self.addObserver(Notificator.onItemClickToInventory, self._onItemClickToInventory)
        self.addObserver(Notificator.onInventoryActivate, self._onInventoryActivate)
        self.addObserver(Notificator.onInventoryDeactivate, self._onInventoryDeactivate)
        pass

    def _onInventoryDeactivate(self, inventory):
        self._cleanAll()
        return False
        pass

    def _onInventoryActivate(self, inventory):
        StateManager.changeState("StateInventory", "INVENTORY_UP")
        return False
        pass

    def _onItemClickToInventory(self, inventory, inventoryItem):
        #        if TaskManager.existTaskChain("INVENTORY_MOVEADDITEM"):
        #            TaskManager.cancelTaskChain("INVENTORY_MOVEADDITEM")
        #            pass

        InventoryEntity = self.Inventory.getEntity()
        InventoryEntity.disableButton()

        #        with TaskManager.createTaskChain(Name = "INVENTORY_MOVEADDITEM", Group = self.Inventory) as tc:
        with TaskManager.createTaskChain(Group=self.Inventory) as tc:
            with tc.addRaceTask(2) as (tc_item, tc_move):
                tc_item.addListener(Notificator.onItemClickToInventory)

                tc_move.addTask("AliasInventorySlotsMoveAddItem", Inventory=self.Inventory, InventoryItem=inventoryItem)
                tc_move.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_UP")

        return False

    def _onStateChange(self, id, value):
        if id != "StateInventory":
            return False

        self.inventoryState = value

        if self.Inventory.isActive() is False:
            return False

        for chain in self.listChain:
            if TaskManager.existTaskChain(chain):
                TaskManager.cancelTaskChain(chain)

        InventoryEntity = self.Inventory.getEntity()

        if value == "INVENTORY_UP":
            with TaskManager.createTaskChain(Name="INVENTORY_UP", Group=self.Inventory) as tc:
                tc.addFunction(InventoryEntity._updateButtonInteractive)
                with tc.addRaceTask(4) as (tc_left, tc_right, tc_item, tc_invItem):
                    tc_left.addTask("TaskButtonClick", ButtonName="Button_InvLeft", AutoEnable=False)
                    tc_left.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_LEFT")

                    tc_right.addTask("TaskButtonClick", ButtonName="Button_InvRight", AutoEnable=False)
                    tc_right.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_RIGHT")

                    tc_item.addListener(Notificator.onItemClickToInventory)

                    tc_invItem.addListener(Notificator.onInventoryPickInventoryItem)
                    tc_invItem.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_ARROWITEM")
                    pass

                pass
            return False

        elif value == "INVENTORY_LEFT":
            with TaskManager.createTaskChain(Name="INVENTORY_LEFT", Group=self.Inventory) as tc:
                tc.addTask("AliasInventorySlotsMoveRight", Inventory=self.Inventory)
                tc.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_UP")
            return False

        elif value == "INVENTORY_RIGHT":
            with TaskManager.createTaskChain(Name="INVENTORY_RIGHT", Group=self.Inventory) as tc:
                tc.addTask("AliasInventorySlotsMoveLeft", Inventory=self.Inventory)
                tc.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_UP")
            return False

        elif value == "INVENTORY_ADDITEM":
            #            with TaskManager.createTaskChain(Name = "INVENTORY_ADDITEM", Group = self.Inventory) as tc:
            #                tc.addListener("onItemClickToInventory")
            #                tc.addTask("TaskStateMutex", ID = "StateInventory", From = "INVENTORY_UP")
            #                with tc.addRaceTask(2) as (tc_move, tc_item):
            #                    tc_move.addTask("TaskStateMutex", ID = "StateInventory", From = "INVENTORY_UP")
            #
            #                    tc_item.addListener("onItemClickToInventory")
            #                    pass

            #                pass
            return False

        elif value == "INVENTORY_ARROWITEM":
            with TaskManager.createTaskChain(Name="INVENTORY_ARROWITEM", Group=self.Inventory) as tc:
                with tc.addRaceTask(2) as (tc_return, tc_remove):
                    tc_return.addListener(Notificator.onInventoryClickReturnItem)
                    tc_return.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_RETURNITEM")

                    tc_remove.addListener(Notificator.onInventoryClickRemoveItem)
                    tc_remove.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_REMOVEITEM")
            return False

        elif value == "INVENTORY_RETURNITEM":
            with TaskManager.createTaskChain(Name="INVENTORY_RETURNITEM", Group=self.Inventory) as tc:
                with tc.addRaceTask(2) as (tc_move, tc_item):
                    tc_move.addListener(Notificator.onInventoryReturnInventoryItem)
                    tc_move.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_UP")

                    tc_item.addListener(Notificator.onItemClickToInventory)
            return False

        elif value == "INVENTORY_REMOVEITEM":
            with TaskManager.createTaskChain(Name="INVENTORY_REMOVEITEM", Group=self.Inventory) as tc:
                with tc.addRaceTask(2) as (tc_move, tc_item):
                    tc_move.addListener(Notificator.onInventoryRemoveInventoryItem)
                    tc_move.addTask("TaskStateChange", ID="StateInventory", Value="INVENTORY_UP")

                    tc_item.addListener(Notificator.onItemClickToInventory)
            return False

        else:
            Trace.log("System", 0, "SystemInventoryMovie _onStateChange: unidentified inventoryState %s" % self.inventoryState)

        return False

    def _onStop(self):
        self._cleanAll()
        pass
    def _cleanAll(self):
        for chain in self.listChain + self.listChain2:
            if TaskManager.existTaskChain(chain):
                TaskManager.cancelTaskChain(chain)
