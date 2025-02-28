from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.StateManager import StateManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.Entities.InventoryFX.InventoryFXManager import InventoryFXManager


class SystemInventoryFX(System):
    def _onParams(self, params):
        super(SystemInventoryFX, self)._onParams(params)

        self.Inventory = params.get("Inventory", DemonManager.getDemon("Inventory"))
        self.EnableScrolling = True
        self.prepare = False

        self.inventoryState = None

        self.listChain = [
            "INVENTORY_UP",
            "INVENTORY_RIGHT",
            "INVENTORY_ADDITEM",
            "INVENTORY_SHOWADD",
            "INVENTORY_ARROWITEM",
            "INVENTORY_RETURNITEM",
            "INVENTORY_REMOVEITEM"
        ]
        self.listChain2 = ["INVENTORY_MOVEADDITEM", "INVENTORY_MOVEDELITEM", "INVENTORY_LEFT", "INVENTORY_RIGHT"]

        self.listChain3 = ["INVENTORY_HIDE", "Inventory_SHOW", "Inventory_DelayHide"]

        self.nextState = None
        self.nextItem = None
        self.blockDown = True
        self.hasBlock = False
        self.nextAction = None

        self.actions = []
        pass

    def getInventoryState(self):
        return self.inventoryState
        pass

    def _onRun(self):
        if self.Inventory.hasObject("Movie_Block") is True:
            self.hasBlock = True
            self.blockDown = DefaultManager.getDefaultBool("InventoryFXStartBlock", False)

            Movie_UnblockDown = self.Inventory.getObject("Movie_UnblockDown")
            Movie_UnblockDown.setEnable(False)

            Movie_UnblockUp = self.Inventory.getObject("Movie_UnblockUp")
            Movie_UnblockUp.setEnable(False)

            Movie_Block = self.Inventory.getObject("Movie_Block")
            Movie_Block.setEnable(False)
            Movie_Unblock = self.Inventory.getObject("Movie_Unblock")
            Movie_Unblock.setEnable(False)

            self.__blockDown(self.blockDown)
            pass

        if self.Inventory.hasObject("Socket_InventoryUp") is True:
            Socket_InventoryUp = self.Inventory.getObject("Socket_InventoryUp")
            Socket_InventoryDown = self.Inventory.getObject("Socket_InventoryDown")

            Socket_InventoryUp.setBlock(True)
            Socket_InventoryUp.setInteractive(True)
            Socket_InventoryDown.setBlock(True)
            Socket_InventoryDown.setInteractive(True)
            pass

        inventoryState = StateManager.getState("StateInventory")
        self._onStateChange("StateInventory", inventoryState)
        self.__updateBlockHide(True)

        self.addObserver(Notificator.onStateChange, self._onStateChange)
        self.addObserver(Notificator.onInventoryDeactivate, self.__onInventoryDeactivate)
        self.addObserver(Notificator.onInventoryFXActionEnd, self.__onInventoryFXActionEnd)

        return True
        pass

    def __blockDown(self, value):
        self.blockDown = value

        if self.hasBlock is False:
            return
            pass

        if TaskManager.existTaskChain("InventoryBlockDown"):
            TaskManager.cancelTaskChain("InventoryBlockDown")
            pass

        Movie_Block = self.Inventory.getObject("Movie_Block")
        Movie_Block.setEnable(not value)

        Movie_Unblock = self.Inventory.getObject("Movie_Unblock")
        Movie_Unblock.setEnable(value)

        with TaskManager.createTaskChain(Name="InventoryBlockDown", Group=self.Inventory) as tc:
            if value is True:
                tc.addEnable(Movie_Block)
                tc.addDisable(Movie_Unblock)
                tc.addTask("TaskEnable", ObjectName="Movie_UnblockUp", Value=False)
                tc.addTask("TaskEnable", ObjectName="Movie_UnblockDown", Value=False)
                tc.addTask("TaskMovieLastFrame", Movie=Movie_Block, Value=False)
                tc.addTask("TaskMoviePlay", Movie=Movie_Block)
                pass
            else:
                tc.addEnable(Movie_Unblock)
                tc.addDisable(Movie_Block)
                tc.addTask("TaskMovieLastFrame", Movie=Movie_Unblock, Value=False)
                tc.addTask("TaskMoviePlay", Movie=Movie_Unblock)
                pass
            pass
        pass

    def __moveBlockUp(self):
        if self.hasBlock is False:
            return
            pass
        if TaskManager.existTaskChain("moveBlocUp"):
            return
            pass
        with TaskManager.createTaskChain(Name="moveBlocUp", Group=self.Inventory) as tc:
            tc.addTask("TaskEnable", ObjectName="Movie_UnblockDown", Value=False)
            tc.addTask("TaskEnable", ObjectName="Movie_UnblockUp", Value=True)
            tc.addTask("TaskMoviePlay", MovieName="Movie_UnblockUp")
            # tc.addTask("TaskEnable", ObjectName = "Movie_UnblockUp", Value = False)
            # tc.addTask("TaskMovieLastFrame", MovieName = "Movie_Unblock", Value = False)
            # tc.addTask("TaskEnable", ObjectName = "Movie_Unblock", Value = True)
            pass
        pass

    def __moveBlockDown(self):
        if self.hasBlock is False:
            return
            pass
        if TaskManager.existTaskChain("moveBlockDown"):
            TaskManager.cancelTaskChain("moveBlockDown")
            pass
        with TaskManager.createTaskChain(Name="moveBlockDown", Group=self.Inventory) as tc:
            tc.addTask("TaskEnable", ObjectName="Movie_Block", Value=False)
            tc.addTask("TaskEnable", ObjectName="Movie_Unblock", Value=False)
            tc.addTask("TaskEnable", ObjectName="Movie_UnblockDown", Value=True)
            tc.addTask("TaskEnable", ObjectName="Movie_UnblockUp", Value=False)
            tc.addTask("TaskMoviePlay", MovieName="Movie_UnblockDown")
            pass
        pass

    def __blockUp(self):  # state up
        if TaskManager.existTaskChain("moveBlockDown"):
            TaskManager.cancelTaskChain("moveBlockDown")
            pass
        if TaskManager.existTaskChain("moveBlocUp"):
            TaskManager.cancelTaskChain("moveBlocUp")
            pass
        with TaskManager.createTaskChain(Group=self.Inventory) as tc:
            tc.addTask("TaskEnable", ObjectName="Movie_UnblockUp", Value=False)
            tc.addTask("TaskMovieLastFrame", MovieName="Movie_UnblockDown", Value=False)
            tc.addTask("TaskEnable", ObjectName="Movie_UnblockDown", Value=True)
            pass
        pass

    # def __onInventoryActivate(self, inventory):
    #     # StateManager.changeState("StateInventory", "INVENTORY_UP")
    #     # Notification.notify(Notificator.onInventoryShow)
    #     return True
    #     pass

    def __onInventoryDeactivate(self, inventory):
        if self.nextAction is not None:
            self.nextAction.onSkip()
            pass
        return False
        pass

    def __setState(self, stateId, *args):
        # print "__setState stateId =", stateId, "args =", args
        self.nextState = stateId
        self.nextStateArgs = args
        pass

    def __onInventoryFXActionEnd(self, action, inventory, invItem, itemName):
        # print "__onInventoryFXActionEnd", len(self.actions)
        if action not in self.actions:
            return False
            pass

        self.actions.remove(action)
        self.nextAction = None
        if len(self.actions) > 0:
            self.nextAction = self.actions[0]
            self.nextAction.onAction()
            pass

        self.__updateButtonInteractive()
        return False
        pass

    def __changeState(self, isSkip):
        # print "5555555__changeState", self.nextState
        # print
        # print "[ SystemInventoryFX ] __changeState() "
        # print "* nextState =", self.nextState
        # print "* Args =", self.nextStateArgs
        # print "* * *"

        if self.nextState == "INVENTORY_ADDITEM":
            # print "INVENTORY_ADDITEM", self.nextStateArgs, len(self.actions)
            type = self.nextStateArgs[3]
            invAction = InventoryFXManager.createAction(type, *self.nextStateArgs)
            self.actions.append(invAction)

            invAction.onRun()
            if len(self.actions) == 1:
                # print "dadadadadadad", type
                invAction.onAction()
                pass
            # else:
            # print "NOOOO", len(self.actions) == 1, len(self.actions)
            # pass
            pass
        elif self.nextState == "INVENTORY_REMOVEITEM":
            # print "INVENTORY_REMOVEITEM", self.nextStateArgs, len(self.actions)
            type = self.nextStateArgs[2]
            invAction = InventoryFXManager.createAction(type, *self.nextStateArgs)
            self.actions.append(invAction)

            invAction.onRun()
            if len(self.actions) == 1:
                invAction.onAction()
                pass
            pass

        StateManager.changeState("StateInventory", self.nextState, *self.nextStateArgs)
        pass

    def __onItemClickToInventory(self, scope, *args):
        # print "__onItemClickToInventory", args
        ######################### old
        # state = args[0]
        # print " __onItemClickToInventory state =", state
        # scope.addTask("TaskFunction", Fn = self.__setState, Args = (state, ) + args, )
        ######################### new

        ######################
        scope.addFunction(self.__setState, "INVENTORY_ADDITEM", "INVENTORY_ADDITEM", *args)
        ######################

        return True
        pass

    def __onInventoryClickRemoveItem(self, scope, *args):
        # print "__onInventoryClickRemoveItem", args
        scope.addFunction(self.__setState, "INVENTORY_REMOVEITEM", *args)

        return True
        pass

    def _onStateChange(self, id, value, *args):
        if id != "StateInventory":
            return False
            pass

        # print "_onStateChange%%%%%", value, args
        # print
        # print "[ SystemInventoryFX ] _onStateChange()"
        # print "* id =", id
        # print "* value =", value
        # print "* args =", args
        # print "* * *"

        self.inventoryState = value

        # if self.Inventory.hasEntity() is False:
        #     return False
        #     pass

        # print self.blockDown, self.hasBlock

        def __thisInventory(inv):
            if inv is not self.Inventory:
                return False
                pass
            return True
            pass

        if value == "INVENTORY_UP":
            with TaskManager.createTaskChain(Name="INVENTORY_UP", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addTask("TaskGameSceneInit", LayerScene="Inventory")
                tc.addTask("TaskEnable", ObjectName="Movie_Hide", Value=False)
                tc.addTask("TaskEnable", ObjectName="Movie_Show", Value=False)
                tc.addTask("TaskEnable", ObjectName="Movie_Slots", Value=True)
                tc.addFunction(self.Inventory.updateSlotsMovie, "Movie_Slots", True)
                tc.addFunction(self.__updateButtonInteractive)
                tc.addFunction(self.__updateBlockInteractive, True)
                if self.blockDown is False and self.hasBlock is True:
                    with tc.addRaceTask(7) as (tc_left, tc_right, tc_item, tc_remove, tc_invItem, tc_down, tc_block):
                        tc_left.addTask("TaskButtonClick", ButtonName="Button_InvLeft", AutoEnable=False)
                        tc_left.addFunction(self.__setState, "INVENTORY_LEFT")

                        tc_right.addTask("TaskButtonClick", ButtonName="Button_InvRight", AutoEnable=False)
                        tc_right.addFunction(self.__setState, "INVENTORY_RIGHT")

                        # tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))
                        tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory)

                        tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)

                        tc_invItem.addListener(Notificator.onInventoryPickInventoryItem, Filter=__thisInventory)
                        tc_invItem.addFunction(self.__setState, "INVENTORY_ARROWITEM")

                        tc_down.addTask("TaskSocketLeave", SocketName="Socket_Hide")
                        tc_down.addFunction(self.__setState, "Inventory_DelayHide")

                        tc_block.addTask("TaskSocketClick", SocketName="Socket_BlockDown", AutoEnable=False)
                        tc_block.addFunction(self.__blockDown, True)
                        tc_block.addFunction(self.__setState, "INVENTORY_UP")
                        pass
                    pass

                elif self.blockDown is True and self.hasBlock is False:
                    with tc.addRaceTask(5) as (tc_left, tc_right, tc_item, tc_remove, tc_invItem):
                        tc_left.addTask("TaskButtonClick", ButtonName="Button_InvLeft", AutoEnable=False)
                        tc_left.addFunction(self.__setState, "INVENTORY_LEFT")

                        tc_right.addTask("TaskButtonClick", ButtonName="Button_InvRight", AutoEnable=False)
                        tc_right.addFunction(self.__setState, "INVENTORY_RIGHT")

                        # tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))
                        tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory)
                        # tc_item.addTask("TaskScopeListener", ID = Notificator.onItemClickToInventory, Scope = self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))

                        tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)

                        tc_invItem.addListener(Notificator.onInventoryPickInventoryItem, Filter=__thisInventory)
                        tc_invItem.addFunction(self.__setState, "INVENTORY_ARROWITEM")
                        pass
                    pass
                else:
                    with tc.addRaceTask(6) as (tc_left, tc_right, tc_item, tc_remove, tc_invItem, tc_block):
                        tc_left.addTask("TaskButtonClick", ButtonName="Button_InvLeft", AutoEnable=False)
                        tc_left.addFunction(self.__setState, "INVENTORY_LEFT")

                        tc_right.addTask("TaskButtonClick", ButtonName="Button_InvRight", AutoEnable=False)
                        tc_right.addFunction(self.__setState, "INVENTORY_RIGHT")

                        # tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))
                        tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory)

                        tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)

                        tc_invItem.addListener(Notificator.onInventoryPickInventoryItem, Filter=__thisInventory)
                        tc_invItem.addFunction(self.__setState, "INVENTORY_ARROWITEM")

                        tc_block.addTask("TaskSocketClick", SocketName="Socket_BlockDown", AutoEnable=False)
                        tc_block.addFunction(self.__blockDown, False)
                        tc_block.addFunction(self.__setState, "INVENTORY_UP")
                        pass
                    pass
                pass

            return False
            pass
        elif value == "Inventory_DelayHide":
            InventoryDelayHide = DefaultManager.getDefaultFloat("InventoryDelayHide", 1)
            InventoryDelayHide *= 1000  # speed fix
            with TaskManager.createTaskChain(Name="Inventory_DelayHide", Group=self.Inventory, Cb=self.__changeState) as tc:
                with tc.addRaceTask(5) as (tc_up, tc_item, tc_remove, tc_delay, tc_leave):
                    tc_up.addTask("TaskSocketEnter", SocketName="Socket_Hide")
                    tc_up.addFunction(self.__setState, "INVENTORY_UP")

                    # tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))
                    tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory)

                    tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)

                    tc_delay.addDelay(InventoryDelayHide, Skiped=False)
                    tc_delay.addFunction(self.__setState, "INVENTORY_HIDE")

                    tc_leave.addListener(Notificator.onInventoryDeactivate)
                    tc_leave.addFunction(self.__setState, "INVENTORY_UP")
                    pass
                pass
            return False
            pass
        elif value == "INVENTORY_HIDE":
            with TaskManager.createTaskChain(Name="INVENTORY_HIDE", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addFunction(self.__moveBlockDown)
                tc.addFunction(self.__updateButtonInteractive, False)
                tc.addFunction(self.__updateBlockInteractive, False)
                tc.addFunction(self.__updateBlockHide, False)
                tc.addTask("TaskEnable", ObjectName="Movie_Hide", Value=True)
                tc.addFunction(self.Inventory.updateSlotsMovie, "Movie_Hide", False)
                tc.addTask("TaskEnable", ObjectName="Movie_Slots", Value=False)
                tc.addNotify(Notificator.onInventoryHide)
                tc.addTask("TaskMoviePlay", MovieName="Movie_Hide", Wait=False)

                with tc.addRaceTask(3) as (tc_item, tc_3, tc_remove):
                    # tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))
                    tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory)
                    tc_item.addTask("TaskEnable", ObjectName="Movie_Hide", Value=False)
                    tc_item.addNotify(Notificator.onInventoryUp)
                    tc_item.addFunction(self.__blockUp)
                    tc_item.addTask("TaskEnable", ObjectName="Movie_Slots", Value=True)
                    tc_item.addFunction(self.Inventory.updateSlotsMovie, "Movie_Slots", True)
                    tc_item.addTask("TaskEnable", ObjectName="Movie_Show", Value=False)

                    tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)
                    tc_remove.addTask("TaskEnable", ObjectName="Movie_Hide", Value=False)
                    tc_remove.addNotify(Notificator.onInventoryUp)
                    tc_remove.addFunction(self.__blockUp)
                    tc_remove.addTask("TaskEnable", ObjectName="Movie_Slots", Value=True)
                    tc_remove.addFunction(self.Inventory.updateSlotsMovie, "Movie_Slots", True)
                    tc_remove.addTask("TaskEnable", ObjectName="Movie_Show", Value=False)

                    tc_3.addTask("TaskMovieEnd", MovieName="Movie_Hide")
                    tc_3.addTask("TaskSetParam", ObjectName="Movie_Hide", Param="Play", Value=False)
                    tc_3.addTask("TaskEnable", ObjectName="Movie_Hide", Value=False)
                    tc_3.addTask("TaskEnable", ObjectName="Movie_Show", Value=True)
                    tc_3.addTask("TaskMovieLastFrame", MovieName="Movie_Show", Value=False)
                    tc_3.addTask("TaskSocketEnter", SocketName="Socket_Show")
                    tc_3.addTask("TaskMovieStop", MovieName="Movie_Hide")
                    tc_3.addTask("TaskEnable", ObjectName="Movie_Hide", Value=False)
                    tc_3.addFunction(self.__setState, "INVENTORY_SHOW")
                    pass
                pass
            pass
        elif value == "INVENTORY_SHOW":
            with TaskManager.createTaskChain(Name="INVENTORY_SHOW", Group=self.Inventory, Cb=self.__changeState) as tc:
                with tc.addRaceTask(3) as (tc_1, tc_item, tc_remove):
                    tc_1.addFunction(self.__moveBlockUp)
                    tc_1.addTask("TaskEnable", ObjectName="Movie_Show", Value=True)
                    tc_1.addFunction(self.Inventory.updateSlotsMovie, "Movie_Show", False)
                    tc_1.addFunction(self.__updateBlockHide, True)
                    tc_1.addNotify(Notificator.onInventoryShow)
                    tc_1.addTask("TaskMoviePlay", MovieName="Movie_Show")
                    tc_1.addTask("TaskEnable", ObjectName="Movie_Show", Value=False)
                    tc_1.addFunction(self.__setState, "INVENTORY_UP")

                    # tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))
                    tc_item.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory)
                    tc_item.addTask("TaskMovieEnd", MovieName="Movie_Show")

                    tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)
                    # tc_remove.addTask("TaskMovieEnd", MovieName = "Movie_Show")
                    pass
                pass
            pass

        elif value == "INVENTORY_LEFT":
            with TaskManager.createTaskChain(Name="INVENTORY_LEFT", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addFunction(self.__updateButtonInteractive, False)
                tc.addTask("AliasInventorySlotsMoveRight", Inventory=self.Inventory)

                tc.addFunction(self.__setState, "INVENTORY_UP")
                pass

            return False
            pass
        elif value == "INVENTORY_RIGHT":
            with TaskManager.createTaskChain(Name="INVENTORY_RIGHT", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addFunction(self.__updateButtonInteractive, False)
                tc.addTask("AliasInventorySlotsMoveLeft", Inventory=self.Inventory)

                tc.addFunction(self.__setState, "INVENTORY_UP")
                pass

            return False
            pass
        elif value == "INVENTORY_ADDITEM":
            with TaskManager.createTaskChain(Name="INVENTORY_ADDITEM", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addFunction(self.__updateButtonInteractive, False)
                with tc.addRaceTask(3) as (tc_add, tc_new, tc_remove):
                    tc_add.addListener(Notificator.onInventoryFXActionEnd)
                    tc_add.addFunction(self.__setState, "INVENTORY_UP")

                    # tc_new.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory, Args = ("INVENTORY_ADDITEM", ))
                    tc_new.addScopeListener(Notificator.onItemClickToInventory, self.__onItemClickToInventory)

                    tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)
                    pass
                pass
        elif value == "INVENTORY_ARROWITEM":
            with TaskManager.createTaskChain(Name="INVENTORY_ARROWITEM", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addFunction(self.__updateButtonInteractive, False)

                with tc.addRaceTask(2) as (tc_return, tc_remove):
                    tc_return.addListener(Notificator.onInventoryClickReturnItem)
                    tc_return.addFunction(self.__setState, "INVENTORY_RETURNITEM")

                    tc_remove.addScopeListener(Notificator.onInventoryClickRemoveItem, self.__onInventoryClickRemoveItem)
                    pass

            return False
            pass
        elif value == "INVENTORY_RETURNITEM":
            with TaskManager.createTaskChain(Name="INVENTORY_RETURNITEM", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addListener(Notificator.onInventoryReturnInventoryItem)

                tc.addFunction(self.__setState, "INVENTORY_UP")
                pass

            return False
            pass
        elif value == "INVENTORY_REMOVEITEM":
            with TaskManager.createTaskChain(Name="INVENTORY_REMOVEITEM", Group=self.Inventory, Cb=self.__changeState) as tc:
                tc.addListener(Notificator.onInventoryRemoveInventoryItem)

                tc.addFunction(self.__setState, "INVENTORY_UP")
                pass
            pass


        else:
            # print "SystemInventoryFX _onStateChange: unidentified inventoryState", self.inventoryState
            pass
        pass

        return False
        pass

    def __updateButtonInteractive(self, value=None):
        Button_InvLeft = self.Inventory.getObject("Button_InvLeft")
        Button_InvRight = self.Inventory.getObject("Button_InvRight")

        CurrentSlotIndex = self.Inventory.getCurrentSlotIndex()

        SlotCount = self.Inventory.getSlotCount()

        # print "__updateButtonInteractive", CurrentSlotIndex, SlotCount

        InventoryItems = self.Inventory.getInventoryItems()
        InventoryItemsCount = len(InventoryItems)

        Button_InvLeft.setEnable(False)
        Button_InvRight.setEnable(False)

        LeftInteractive = 0
        RightInteractive = 0
        if value is False:
            Button_InvLeft.setParam("Interactive", LeftInteractive)
            Button_InvRight.setParam("Interactive", RightInteractive)
            return
            pass

        if CurrentSlotIndex > 0:
            LeftInteractive = 1
            Button_InvLeft.setEnable(True)
            pass

        if CurrentSlotIndex + SlotCount < InventoryItemsCount:
            RightInteractive = 1
            Button_InvRight.setEnable(True)
            pass

        Button_InvLeft.setParam("Interactive", LeftInteractive)
        Button_InvRight.setParam("Interactive", RightInteractive)
        pass

    def __updateBlockInteractive(self, value):
        if self.hasBlock is True:
            Socket_BlockDown = self.Inventory.getObject("Socket_BlockDown")
            Socket_BlockDown.setParam("Interactive", value)
            pass
        pass

    def __updateBlockHide(self, value):
        if self.Inventory.hasObject("Socket_InventoryUp") is False:
            return
            pass

        Socket_InventoryUp = self.Inventory.getObject("Socket_InventoryUp")
        Socket_InventoryDown = self.Inventory.getObject("Socket_InventoryDown")
        if value is False:
            Socket_InventoryUp.setEnable(False)
            Socket_InventoryDown.setEnable(True)
            pass
        else:
            Socket_InventoryUp.setEnable(True)
            Socket_InventoryDown.setEnable(False)
            pass
        pass

    def _onStop(self):
        for chain in self.listChain + self.listChain2 + self.listChain3:
            if TaskManager.existTaskChain(chain):
                TaskManager.cancelTaskChain(chain)
                pass
            pass

        if TaskManager.existTaskChain("InventoryBlockDown"):
            TaskManager.cancelTaskChain("InventoryBlockDown")
            pass
        if TaskManager.existTaskChain("moveBlockDown"):
            TaskManager.cancelTaskChain("moveBlockDown")
            pass
        if TaskManager.existTaskChain("moveBlocUp"):
            TaskManager.cancelTaskChain("moveBlocUp")
            pass
        pass

    pass
