from Event import Event
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.InventoryPanelManager import InventoryPanelManager
from HOPA.SemaphoreManager import SemaphoreManager
from Holder import Holder


# fixme: guard block input can't save as from game closing through window closing, possibly can corrupt save games


class SystemInventoryPanel(System):
    tc_Inventory_finish_event = None

    def __init__(self):
        super(SystemInventoryPanel, self).__init__()
        self.tc_Inventory = None
        self.CurrentInventory = None
        self.param = None
        self.scene_cached_inv_data = {}

        self.zoom_repeat_cached_inv_data = {}
        self.zoom_repeat_tcs = {}
        self.CurrentScene = None

    def _onRun(self):
        SystemInventoryPanel.tc_Inventory_finish_event = Event('SystemInventoryPanelSwapFinish')

        self.param = InventoryPanelManager.getData()

        self.addObserver(Notificator.onInventoryChage, self.InventorySwap)
        self.addObserver(Notificator.onSceneInit, self.InventoryChange)
        self.addObserver(Notificator.onSceneLeave, self.__cbOnSceneLeave)

        return True

    def __cbOnSceneLeave(self, _scene_name, *_):
        if self.tc_Inventory is not None:
            self.tc_Inventory.cancel()
            self.tc_Inventory = None

        return False

    def InventoryChange(self, SceneName):
        self.CurrentScene = SceneName

        if SceneName not in self.scene_cached_inv_data:
            return False

        self.CurrentInventory = self.getActiveInventoryName()
        if self.CurrentInventory is None:
            return False

        InventoryName = self.scene_cached_inv_data[SceneName]

        if _DEVELOPMENT is True:
            Trace.msg("<SystemInventoryPanel> InventoryChange from {!r} to {!r}".format(self.CurrentInventory, InventoryName))

        SceneManager.disableSceneLayerGroup(self.CurrentScene, self.CurrentInventory)
        SceneManager.enableSceneLayerGroup(self.CurrentScene, InventoryName)
        SystemInventoryPanel.tc_Inventory_finish_event()

        return False

    def setCurrentInventory(self, inventory_getter):
        self.CurrentInventory = inventory_getter()

    def getCurrentInventory(self):
        return self.CurrentInventory

    def getActiveInventoryName(self):
        for group_name in self.param:
            group = GroupManager.getGroup(group_name)
            if group.getEnable():
                return group_name

    def getActiveInventoryObject(self):
        for group_name in self.param:
            group = GroupManager.getGroup(group_name)

            if not group.getEnable():
                continue

            if not DemonManager.hasDemon(group_name):
                continue

            return DemonManager.getDemon(group_name)

    def __swapInventoryScope(self, source, inventory_to_getter=lambda: False):
        inventory_from = self.getActiveInventoryName()
        if inventory_from is None:
            return

        inventory_to = inventory_to_getter()
        if not bool(inventory_to):
            return

        if inventory_to == inventory_from:
            return

        sys_inv_fold = SystemManager.getSystem('SystemInventoryFold')
        check_box_lock = GroupManager.getObject("InventoryLock", "Movie2CheckBox_Lock")
        semaphore_inv_fold_interrupt = SemaphoreManager.getSemaphore('SemaphoreSysInvFoldInterrupt')

        check_box_lock_prev_val_holder = Holder()

        source.addFunction(lambda: check_box_lock_prev_val_holder.set(bool(check_box_lock.getValue())))
        source.addFunction(check_box_lock.setBlockState, True)
        source.addFunction(check_box_lock.setValue, True)
        source.addSemaphore(semaphore_inv_fold_interrupt, To=True)  # block inv fold

        with source.addIfTask(lambda: sys_inv_fold.Working) as (true, _):
            with true.addRaceTask(2) as (race_0, race_1):  # here we wait inv fold to stop
                race_0.addListener(Notificator.onInventoryFold_Complete)
                race_1.addListener(Notificator.onInventoryRise_Complete)

        '''  Without Block Input '''
        # with source.addIfTask(lambda: sys_inv_fold.State) as (true, false):
        #     true.addScope(self.scopeHide, inventory_from)
        #
        #     false.addFunction(lambda: sys_inv_fold.Change_State(True))
        #
        # source.addTask("TaskSceneLayerGroupEnable", LayerName=inventory_from, Value=False)
        # source.addTask("TaskSceneLayerGroupEnable", LayerName=inventory_to, Value=True)
        # source.addScope(self.scopeShow, inventory_to)
        ''' '''

        ''' With Block Input '''
        with GuardBlockInput(source) as guard_source:
            with guard_source.addIfTask(lambda: sys_inv_fold.State) as (true, false):
                true.addScope(self.scopeHide, inventory_from)

                false.addFunction(lambda: sys_inv_fold.Change_State(True))

            guard_source.addTask("TaskSceneLayerGroupEnable", LayerName=inventory_from, Value=False)
            guard_source.addTask("TaskSceneLayerGroupEnable", LayerName=inventory_to, Value=True)
            guard_source.addScope(self.scopeShow, inventory_to)
        ''' '''

        source.addFunction(lambda: check_box_lock.setValue(check_box_lock_prev_val_holder.get()))
        source.addFunction(check_box_lock.setBlockState, False)
        source.addSemaphore(semaphore_inv_fold_interrupt, To=False)  # unblock inv fold

    def InventorySwap(self, InventoryName, onZoomRepeat=False, zoomGroupName='', onLoad=False):
        if _DEVELOPMENT is True:
            Trace.msg("<SystemInventoryPanel> InventorySwap: Inv={!r}, ZoomRepeat={}, ZoomGroup={!r}, onLoad={}".format(
                InventoryName, onZoomRepeat, zoomGroupName, onLoad))

        if self.CurrentInventory is None:
            self.setCurrentInventory(self.getActiveInventoryName)

        '''
        Zoom Repeat Case
        '''
        if onZoomRepeat:
            '''
            Cancel zoom swap inv tc
            '''
            if zoomGroupName in self.zoom_repeat_cached_inv_data:
                self.zoom_repeat_cached_inv_data.pop(zoomGroupName)
                self.zoom_repeat_tcs[zoomGroupName].cancel()

                if self.tc_Inventory is not None:
                    if self.tc_Inventory.state is self.tc_Inventory.RUN:
                        return False

                with TaskManager.createTaskChain() as tc:
                    tc.addScope(self.__swapInventoryScope, lambda: InventoryName)
                return False

            '''
            Create zoom inv swap tc
            '''
            self.zoom_repeat_cached_inv_data[zoomGroupName] = InventoryName

            tc = TaskManager.createTaskChain()
            self.zoom_repeat_tcs[zoomGroupName] = tc

            with tc as tc:
                if self.tc_Inventory is not None:
                    if self.tc_Inventory.state is self.tc_Inventory.RUN:
                        tc.addEvent(SystemInventoryPanel.tc_Inventory_finish_event)

                if onLoad:
                    tc.addListener(Notificator.onZoomEnter, Filter=lambda groupName: groupName == zoomGroupName)
                    tc.addFunction(self.setCurrentInventory, self.getActiveInventoryName)

                tc.addScope(self.__swapInventoryScope, lambda: InventoryName)

                with tc.addWhileTask() as source:
                    with source.addRaceTask(2) as (race_scene_leave, race_zoom_leave):
                        race_scene_leave.addListener(Notificator.onSceneLeave)

                        race_zoom_leave.addListener(Notificator.onZoomLeave,
                                                    Filter=lambda groupName: groupName == zoomGroupName)
                        race_zoom_leave.addDelay(0)
                        race_zoom_leave.addScope(self.__swapInventoryScope, self.getCurrentInventory)

                    source.addListener(Notificator.onZoomEnter, Filter=lambda groupName: groupName == zoomGroupName)
                    source.addScope(self.__swapInventoryScope, lambda: InventoryName)

            return False

        '''
        Default manual scene inventory switch
        '''
        self.setCurrentInventory(self.getActiveInventoryName)

        SceneName = SceneManager.getCurrentSceneName()
        if SceneName is None:
            SceneName = SceneManager.getPrevSceneName()
            if _DEVELOPMENT is True:
                Trace.msg("[!] <SystemInventoryPanel> InventorySwap: SceneName is None - can't remember inventory for last scene! Try to use PrevScene {!r} instead of CurScene...".format(SceneName))
        self.scene_cached_inv_data[SceneName] = InventoryName

        InventoryFrom = self.getActiveInventoryName()

        self.tc_Inventory = TaskManager.createTaskChain(Cb=self.tcInventoryCB, CbArgs=(InventoryFrom, InventoryName))
        # self.tc_Inventory = TaskManager.createTaskChain(Cb=lambda _: SystemInventoryPanel.tc_Inventory_finish_event())
        with self.tc_Inventory as tc:
            tc.addScope(self.__swapInventoryScope, lambda: InventoryName)
        return False

    def tcInventoryCB(self, isSkip, InventoryFrom, InventoryTo):
        if isSkip:
            ''' HIDE OLD INVENTORY CB '''
            old_inv = SceneManager.getSceneLayerGroup(self.CurrentScene, InventoryFrom)

            if not old_inv.getEnable():
                old_inv.onEnable()

            old_inv_demon = DemonManager.getDemon(InventoryFrom)
            old_inv_demon_en = old_inv_demon.getEntity()

            if old_inv_demon_en is not None:
                old_inv_demon.setEnable(True)

                Movie_Close = old_inv_demon.getObject("Movie2_Close")
                if Movie_Close is not None:
                    Movie_Close.setLastFrame(True)
                    Movie_Close.setEnable(False)

                Movie_Open = old_inv_demon.getObject("Movie2_Open")
                if Movie_Open is not None:
                    Movie_Open.setLastFrame(False)
                    Movie_Open.setEnable(False)

                Movie_Return = old_inv_demon.getObject("Movie2_Return")
                if Movie_Return is not None:
                    Movie_Return.setEnable(True)

            if old_inv.getEnable():
                old_inv.onDisable()
            ''' '''

            ''' SHOW NEW INVENTORY CB '''
            new_inv = SceneManager.getSceneLayerGroup(self.CurrentScene, InventoryTo)

            if not new_inv.getEnable():
                new_inv.onEnable()

            new_inv_demon = DemonManager.getDemon(InventoryTo)
            new_inv_demon_en = new_inv_demon.getEntity()

            if new_inv_demon_en is not None:
                new_inv_demon.setEnable(True)

                Movie_Close = new_inv_demon.getObject("Movie2_Close")
                if Movie_Close is not None:
                    Movie_Close.setLastFrame(False)
                    Movie_Close.setEnable(True)
            ''' '''

        SystemInventoryPanel.tc_Inventory_finish_event()

    def scopeShow(self, source, inventory_Name):
        name = self.Spiker_Ultimate(inventory_Name)
        demon_Inventory_2 = DemonManager.getDemon(name)

        demon_Inventory_2.setEnable(True)

        entity_Inventory_2 = demon_Inventory_2.getEntity()

        source.addScope(entity_Inventory_2.Show_InventoryPanel)

    def scopeHide(self, source, inventory_Name):
        name = self.Spiker_Ultimate(inventory_Name)
        demon_Inventory_2 = DemonManager.getDemon(name)

        demon_Inventory_2.setEnable(True)

        entity_Inventory_2 = demon_Inventory_2.getEntity()

        source.addScope(entity_Inventory_2.Hide_InventoryPanel)

    @staticmethod
    def Spiker_Ultimate(name):
        if name is "HOGFittingInventory":
            return "HOGInventoryFitting"
        else:
            return name

    def Clean_Full(self):
        if self.tc_Inventory is not None:
            self.tc_Inventory.cancel()
            self.tc_Inventory = None

        for tc in self.zoom_repeat_tcs.values():
            tc.cancel()
        self.zoom_repeat_tcs = {}

    def _onStop(self):
        self.Clean_Full()

    def _onLoad(self, data_save):
        self.scene_cached_inv_data = data_save[0]

        for (zoom_group_name, inventory_name) in data_save[1].items():
            self.InventorySwap(inventory_name, True, zoom_group_name, True)

    def _onSave(self):
        return self.scene_cached_inv_data, self.zoom_repeat_cached_inv_data
