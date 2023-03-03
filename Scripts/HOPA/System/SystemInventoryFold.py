from Foundation.DefaultManager import DefaultManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from HOPA.SemaphoreManager import SemaphoreManager


SYSTEM_INVENTORY_PANEL_NAME = 'SystemInventoryPanel'
DEFAULT_INVENTORY_NAME = 'Inventory'


class SystemInventoryFold(System):
    def __init__(self):
        super(SystemInventoryFold, self).__init__()
        self.tc_Inventory = None
        self.tc = None

        self.Lock = DefaultManager.getDefaultBool("InventoryLock", True)
        self.State = True
        self.Working = False

        self.CurrentSceneName = None
        self.Rise_Value = None
        self.Rise_Value_MaxX = None
        self.Rise_Value_MinX = None
        self.Fold_Value = None
        self.MousePositionProviderID = None

        self.cur_inventory_name = DEFAULT_INVENTORY_NAME

        self.semaphore_sys_inv_fold_tc_interrupt = Semaphore(False, 'SemaphoreSysInvFoldInterrupt')
        SemaphoreManager.addSemaphore(self.semaphore_sys_inv_fold_tc_interrupt)

    @staticmethod
    def __isInventoryFoldingFeatureAllowed():
        return not Mengine.hasTouchpad()

    @staticmethod
    def __disableInventoryLockButton():
        checkBoxLock = GroupManager.getObject("InventoryLock", "Movie2CheckBox_Lock")
        checkBoxLock.setEnable(False)
        buttonBorder = GroupManager.getObject("InventoryLock", "Movie2_Border")
        buttonBorder.setEnable(False)

    def _onRun(self):
        super(SystemInventoryFold, self)._onRun()

        if self.__isInventoryFoldingFeatureAllowed():
            self.addObserver(Notificator.onItemPicked, self.Rise_Inventory_Forced)
            self.addObserver(Notificator.onInventoryAddItem, self.Rise_Inventory_Forced)
            self.addObserver(Notificator.onInventoryRise, self.Rise_Inventory_Forced)
            self.addObserver(Notificator.onSceneInit, self.__onSceneInit)

            self.setup_Lock()
            self.Run_Lock_Tc()

        else:  # if mobile no inventory folding feature, hide buttons
            self.__disableInventoryLockButton()

        return True

    def Run_Lock_Tc(self):
        check_box_lock = GroupManager.getObject("InventoryLock", "Movie2CheckBox_Lock")

        self.tc = TaskManager.createTaskChain(Repeat=True)
        with self.tc as tc:
            tc.addSemaphore(self.semaphore_sys_inv_fold_tc_interrupt, From=False)

            with tc.addRaceTask(3) as (tc_true, tc_false, tc_interrupt):
                tc_false.addTask("TaskMovie2CheckBox", Movie2CheckBox=check_box_lock, Value=False)
                tc_false.addFunction(self.Change_Lock, False)
                tc_false.addFunction(self.setup_Lock)

                tc_true.addTask("TaskMovie2CheckBox", Movie2CheckBox=check_box_lock, Value=True)
                tc_true.addFunction(self.Change_Lock, True)
                tc_true.addFunction(self.setup_Lock)

                tc_interrupt.addSemaphore(self.semaphore_sys_inv_fold_tc_interrupt, From=True)

                with tc_true.addFork() as source_fork:
                    with source_fork.addRaceTask(4) as (tc_1, tc_2, tc_3, tc_4):
                        tc_1.addFunction(self.Rise_Inventory_Forced)
                        tc_1.addListener(Notificator.onInventoryRise_Complete)

                        tc_2.addListener(Notificator.onInventoryFold_Complete)
                        tc_2.addFunction(self.Rise_Inventory_Forced)

                        tc_3.addTask("TaskMovie2CheckBox", Movie2CheckBox=check_box_lock, Value=False)
                        tc_4.addTask("TaskMovie2CheckBox", Movie2CheckBox=check_box_lock, Value=True)

    @staticmethod
    def Setup_Y(socketName):
        movie = GroupManager.getObject('InventoryLock', "Movie2_Border")
        if movie.isActive() is False:
            return

        movie.setEnable(True)
        socket = movie.getSocket(socketName)
        BoundingBox = Mengine.getHotSpotPolygonBoundingBox(socket)
        movie.setEnable(False)

        return BoundingBox.minimum.y

    @staticmethod
    def Setup_X(socketName):
        movie = GroupManager.getObject('InventoryLock', "Movie2_Border")
        if movie.isActive() is False:
            return None, None
        movie.setEnable(True)
        socket = movie.getSocket(socketName)
        BoundingBox = Mengine.getHotSpotPolygonBoundingBox(socket)
        movie.setEnable(False)

        return BoundingBox.minimum.x, BoundingBox.maximum.x

    def Setup(self):
        if self.Rise_Value is None:
            self.Rise_Value = self.Setup_Y("Rise")
            self.Rise_Value_MinX, self.Rise_Value_MaxX = self.Setup_X("Rise")

        if self.Fold_Value is None:
            self.Fold_Value = self.Setup_Y("Fold")

        if self.Rise_Value is not None and self.Fold_Value is not None:
            if self.MousePositionProviderID is None:
                self.MousePositionProviderID = Mengine.addMousePositionProvider(None, None, None, self.__onMousePositionChange)

    def setup_Lock(self):
        check_box_lock = GroupManager.getObject("InventoryLock", "Movie2CheckBox_Lock")
        check_box_lock.setValue(self.Lock)

    def Change_Inventory(self, flag):
        if flag:
            if self.State is False:
                self.Action()

        else:
            if self.State is True and self.Lock is False:
                self.Action()

        return False

    def __onSceneInit(self, SceneName, *_):
        if self.CurrentSceneName == SceneName:
            return False

        self.Setup()
        self.CurrentSceneName = SceneName
        self.Stop_Tc()
        self.Working = True

        self.tc_Inventory = TaskManager.createTaskChain(Repeat=False)
        with self.tc_Inventory as tc:
            if self.State:
                tc.addScope(self.scopeSet_Rised)
            else:
                tc.addScope(self.scopeSet_Folded)
            tc.addFunction(self.Change_Working)

        return False

    def Rise_Inventory_Forced(self, *_):
        if self.State is True:
            return False
        self.Action()
        return False

    def Action(self):
        if self.Working is True:
            return

        Delay = DefaultManager.getDefault("InventoryHideDelayTime", 1) * 1000  # Time Fix
        self.Stop_Tc()
        self.Working = True

        self.tc_Inventory = TaskManager.createTaskChain(Repeat=False)
        with self.tc_Inventory as tc:
            if self.State is True:
                tc.addDelay(Delay)
                tc.addFunction(self.Change_State)
                tc.addScope(self.scopeHide)
                tc.addNotify(Notificator.onInventoryFold_Complete)
                tc.addFunction(self.Change_Working)
            else:
                tc.addFunction(self.Change_State)
                tc.addScope(self.scopeShow)
                tc.addNotify(Notificator.onInventoryRise_Complete)
                tc.addFunction(self.Change_Working)

    def getCurInventoryEntity(self):
        """
        :return: Inventory Entity
        """

        '''
        Try update current inventory name
        '''
        if SystemManager.hasSystem(SYSTEM_INVENTORY_PANEL_NAME):
            system_inventory_panel = SystemManager.getSystem(SYSTEM_INVENTORY_PANEL_NAME)
            active_inventory_name = system_inventory_panel.getActiveInventoryName()

            self.cur_inventory_name = DEFAULT_INVENTORY_NAME if active_inventory_name is None else active_inventory_name

        if not DemonManager.hasDemon(self.cur_inventory_name):
            return

        demon_Inventory = DemonManager.getDemon(self.cur_inventory_name)
        if demon_Inventory.isActive() is False:
            return

        entity_Inventory = demon_Inventory.getEntity()
        return entity_Inventory

    def scopeHide(self, source):
        entity_Inventory = self.getCurInventoryEntity()
        if entity_Inventory is None:
            return

        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName is None:
            self.Change_State()
            return

        source.addScope(entity_Inventory.Folding_Inventory)

    def scopeShow(self, source):
        entity_Inventory = self.getCurInventoryEntity()
        if entity_Inventory is None:
            return

        currentSceneName = SceneManager.getCurrentSceneName()
        if currentSceneName is None:
            self.Change_State()
            return

        source.addScope(entity_Inventory.Rising_Inventory)

    def scopeSet_Rised(self, source):
        entity_Inventory = self.getCurInventoryEntity()
        if entity_Inventory is None:
            return

        source.addFunction(entity_Inventory.Rised_Inventory)

    def scopeSet_Folded(self, source):
        entity_Inventory = self.getCurInventoryEntity()
        if entity_Inventory is None:
            return

        source.addFunction(entity_Inventory.Folded_Up_Inventory)

    def Change_State(self, state=None):
        if state is None:
            self.State = not self.State
        else:
            self.State = state

    def Change_Lock(self, lock=None):
        if lock is None:
            self.Lock = not self.Lock
        else:
            self.Lock = lock

    def Change_Working(self, working=None):
        if working is None:
            self.Working = not self.Working
        else:
            self.Working = working

    def __onMousePositionChange(self, _, position):
        if self.semaphore_sys_inv_fold_tc_interrupt.getValue() is True:
            return

        if position.y < self.Fold_Value:
            self.Change_Inventory(False)
        elif position.y > self.Rise_Value:
            if self.Rise_Value_MinX < position.x < self.Rise_Value_MaxX:
                self.Change_Inventory(True)

    def Stop_Tc(self):
        if self.tc_Inventory is not None:
            self.tc_Inventory.cancel()
            self.tc_Inventory = None

    def Clean_Full(self):
        if self.tc_Inventory is not None:
            self.tc_Inventory.cancel()
            self.tc_Inventory = None

        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        if self.MousePositionProviderID is not None:
            Mengine.removeMousePositionProvider(self.MousePositionProviderID)
            self.MousePositionProviderID = None

        self.Rise_Value = None
        self.Rise_Value_MaxX = None
        self.Rise_Value_MinX = None
        self.Fold_Value = None
        return False

    def _onSave(self):
        super(SystemInventoryFold, self)._onSave()

        return self.Lock, self.State

    def _onLoad(self, data_save):
        super(SystemInventoryFold, self)._onLoad(data_save)

        if data_save is None:
            return
        self.Lock, self.State = data_save

    def _onStop(self):
        super(SystemInventoryFold, self)._onStop()

        self.Clean_Full()
