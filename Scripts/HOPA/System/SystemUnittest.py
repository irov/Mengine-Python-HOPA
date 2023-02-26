from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.ItemManager import ItemManager
from HOPA.UnittestManager import UnittestManager
from Holder import Holder

MENGINE_OPTION_UNITTEST_ENABLE = 'unittest'

class TestActionInterface(object):
    def __init__(self, index, param):
        self.index = index
        self.param = param

    def _scopeAction(self, source):
        return True

    def scopeAction(self, source):
        time = Mengine.getTimeMs()
        # print '\n\t[SystemUnittest] [run] test action id {} type {} first_param {}'.format(
        #     self.index, self.param.test_action, self.param.test_action_params[0])

        rc = self._scopeAction(source)

        def dbgPrint():
            if rc:
                print('\t [SystemUnittest] [success] --{} ms test action id {} type {} first_param {}\n'.format(Mengine.getTimeMs() - time, self.index, self.param.test_action, self.param.test_action_params[0]))
            else:
                print('\t [SystemUnittest] [fail] --{} test action id {} type {} first_param {}\n'.format(Mengine.getTimeMs() - time, self.index, self.param.test_action, self.param.test_action_params[0]))

        source.addFunction(dbgPrint)

# class TestActionKey(TestActionInterface):
#     def __init__(self, index, param):
#         super(TestActionKey, self).__init__(index, param)
#
#     def scopeAction(self, source):
#         print 'todo: scopeAction for TestActionKey'
#         return


class TestActionListener(TestActionInterface):
    def __init__(self, index, param):
        super(TestActionListener, self).__init__(index, param)

        self.notificator_id = Notificator.getIdentity(self.param.test_action_params[0])

    def _scopeAction(self, source):
        source.addTask("TaskListener", ID=self.notificator_id)

class TestActionNotify(TestActionInterface):
    def __init__(self, index, param):
        super(TestActionNotify, self).__init__(index, param)

        self.notificator_id = Notificator.getIdentity(self.param.test_action_params[0])
        self.args = self.param.test_action_params[1:]

    def _scopeAction(self, source):
        source.addTask("TaskNotify", ID=self.notificator_id, Args=self.args)

class TestActionWait(TestActionInterface):
    def __init__(self, index, param):
        super(TestActionWait, self).__init__(index, param)

        self.delay = self.param.test_action_params[0]

    def _scopeAction(self, source):
        source.addDelay(self.delay)
        return True

class TestActionPrint(TestActionInterface):
    def __init__(self, index, param):
        super(TestActionPrint, self).__init__(index, param)

        self.msg = self.param.test_action_params[0]

    def _scopeAction(self, source):
        source.addPrint(self.msg)
        return True

class TestActionTransition(TestActionInterface):
    def __init__(self, index, param):
        super(TestActionTransition, self).__init__(index, param)
        self.scene_name = self.param.test_action_params[0]
        if self.scene_name is None:
            print('todo: trace TestActionTransition first param scene_name is None')

        action_params = self.param.test_action_params
        self.zoom_name = None if len(action_params) < 2 else action_params[1]
        if self.zoom_name == -1:
            self.zoom_name = None

    def _scopeAction(self, source):
        source.addTask("AliasTransition", SceneName=self.scene_name, ZoomGroupName=self.zoom_name)  # second method
        return True

class TestActionClick(TestActionInterface):
    def __init__(self, index, param):
        super(TestActionClick, self).__init__(index, param)

        self.obj_name = self.param.test_action_params[0]

        self.obj = None

        self.obj_group = self.param.test_action_params[1]
        self.obj_parent = self.param.test_action_params[2]
        self.obj_param = self.param.test_action_params[3]
        self.click_speed = self.param.test_action_params[4]
        self.wait_enable = bool(self.param.test_action_params[5])

    def __cbVisitor(self, obj_):
        obj_name = obj_.getName()
        # print '[DBG] __cbVisitor parent: {} obj: {}'.format(
        #     None if not obj_.hasParent() else obj_.getParent().getName(),
        #     obj_.getName())

        if obj_name == self.obj_name:
            # print '[DBG] __cbVisitor obj found', obj_name
            if self.obj_parent != -1:
                parent = obj_.getParent()

                if parent is None:
                    return

                if self.obj_parent != parent.getName():
                    return

            self.obj = obj_

            # print '__cbVisitor found object name {} type {} parent {} position {} enable {}'.format(
            #     obj_.getName(), obj_.getType(), obj_.getParent(), obj_.entity.node.getWorldPosition(), obj_.getEnable()
            # )

            return False

    def __findClickObj(self):
        if self.obj_name is None:
            print('todo: trace testActionClick __obj_name is none')
            return False

        cur_scene = SceneManager.getCurrentScene()

        if self.obj_group != -1:
            group = GroupManager.getGroup(self.obj_group)

            if group is None:
                print('todo: trace testActionClick group with name {} not founded'.format(self.obj_group))

            # # objects id enigmas demon fix maybe todo later
            # if self.obj_parent != -1:
            #     if group.hasObject(self.obj_parent):
            #         object_ = group.getObject(self.obj_parent)
            #         print '???????????????????', object_.getType()

            else:
                rc = group.visitObjectsBrakeOnFalse(self.__cbVisitor)

                # print '[DBG] __findClickObj GROUP "{}" OBJ "{}" VISITOR RC STATUS: {}'.format(
                #     self.obj_group, self.obj_name, rc)

                if self.obj is not None:
                    # dbg_msg_true = '\t[SystemUnittest]testActionCLick found obj to click: {}, obj_type: {} obj_group: {}'. \
                    #     format(self.obj.getName(), self.obj.getType(), self.obj_group)
                    # print dbg_msg_true
                    return True

        for description in cur_scene.groupOrder:
            layer_type = description["Type"]
            if layer_type != "Scene":
                continue

            '''
            if in test action we have defined group, we search only there
            '''
            group_name = description.get("Group")

            group = GroupManager.getGroup(group_name)
            if group is None:
                continue

            rc = group.visitObjectsBrakeOnFalse(self.__cbVisitor)

            # print '[DBG] __findClickObj GROUP "{}" OBJ "{}" VISITOR RC STATUS: {}'.format(
            #     group_name, self.obj_name, rc)

            if self.obj is not None:
                # dbg_msg_true = '\t[SystemUnittest]testActionCLick found obj to click: {}, obj_type: {} obj_group: {}'.\
                #     format(self.obj.getName(), self.obj.getType(), group_name)
                # # print dbg_msg_true
                return True

        # dbg_msg_false = '\t[SystemUnittest]testActionClick can\'t find obj to click for {}'.format(self.obj_name)
        # print dbg_msg_false
        return False

    def _scopeAction(self, source):
        def scopeCruiseControlActionObj(source_):
            with source_.addIfTask(lambda: self.obj is not None) as (true, _):
                true.addTask("AliasCruiseControlAction", Object=self.obj, ObjectParams=[self.obj_param, self.wait_enable], Speed=self.click_speed)

        def scopeCruiseControlActionPos(source_):
            source_.addTask("AliasCruiseControlAction", Position=(self.param.test_action_params[1], self.param.test_action_params[2]), Speed=self.click_speed, )

        if SceneManager.getCurrentScene() is None:
            source.addListener(Notificator.onSceneEnter, Filter=lambda scene_name: scene_name is not None)

        if self.param.test_action_params[0] == 'Position':
            scope_cruise_control_action = scopeCruiseControlActionPos

        else:
            source.addFunction(self.__findClickObj)
            scope_cruise_control_action = scopeCruiseControlActionObj

        source.addScope(scope_cruise_control_action)

        return True

class TestActionAddInventoryItems(TestActionInterface):
    def __init__(self, index, param):
        super(TestActionAddInventoryItems, self).__init__(index, param)

        params = param.test_action_params

        self.inventory = DemonManager.getDemon(params[0])
        self.item_names = params[1:]

    def _scopeAction(self, source):
        for item_name in self.item_names:
            inventory_item = ItemManager.getItemInventoryItem(item_name)

            source.addTask("TaskInventoryAddItem", Inventory=self.inventory, ItemName=item_name)
            source.addTask("TaskInventorySlotAddInventoryItem", Inventory=self.inventory, InventoryItem=inventory_item)
            source.addTask("TaskEnable", Object=inventory_item, Value=True)

        return True

TEST_ACTION_MAP = {'TestActionClick': TestActionClick,  # 'TestActionKey': TestActionKey,
    'TestActionWait': TestActionWait, 'TestActionPrint': TestActionPrint, 'TestActionTransition': TestActionTransition, 'TestActionListener': TestActionListener, 'TestActionNotify': TestActionNotify, 'TestActionAddInventoryItems': TestActionAddInventoryItems}

class SystemUnittest(System):
    s_test_action_units = {}

    def _onParams(self, _params):
        self.tc = None
        self.tc_print_mouse_pos = None

    def _onRun(self):
        if not Mengine.hasOption(MENGINE_OPTION_UNITTEST_ENABLE):
            return True

        SystemUnittest.s_test_actions = {}

        # def dbg():
        #     group = GroupManager.getGroup('02_ShrineHO2')
        #     if group is None:
        #         return
        #
        #     demon = group.getObject('Demon_HOGFitting_02_ShrineHO2')
        #
        #     if demon is None:
        #         return
        #
        #     print 'demon child', [child.getName() for child in demon.child]
        #     print 'demon child_unique', [child.getName() for child in demon.child_unique]
        #
        # with self.createTaskChain(Name='dbg', Repeat=True, Global=True) as tc:
        #     tc.addFunction(dbg)
        #     tc.addDelay(1000)

        self.__loadUnittests()
        self.__runUnittests()

        if UnittestManager.s_print_mouse_pos_vk != -1:
            self.__runPrintMousePosTC()

        return True

    @staticmethod
    def _onSave():
        save_data = dict()
        return save_data

    @staticmethod
    def _onLoad(save_data):
        return

    def _onStop(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        if self.tc_print_mouse_pos is not None:
            self.tc_print_mouse_pos.cancel()
            self.tc_print_mouse_pos = None

    @staticmethod
    def __scopePressKey(source, key_code):
        source.addListener(Notificator.onKeyEvent, lambda key, x, y, isDown, isRepeating: isRepeating is False and isDown is False and key == key_code)

    @staticmethod
    def __printTimestamp(msg, time_getter, *args):
        delta_time = Mengine.getTimeMs() - time_getter()
        delta_time = delta_time / 1000
        print(msg.format(delta_time, *args))

    def __runPrintMousePosTC(self):
        self.tc_print_mouse_pos = TaskManager.createTaskChain(Repeat=True)

        print_key_name = UnittestManager.s_print_mouse_pos_vk
        print_key_code = UnittestManager.getPrintMousePosVK()

        def printMousePos():
            print('[SystemUnittest] Current mouse position is:', Mengine.getCursorPosition())

        with self.tc_print_mouse_pos as tc:
            tc.addPrint('[SystemUnittest] Press "{}" button to print current cursor position'.format(print_key_name))
            tc.addScope(self.__scopePressKey, print_key_code)
            tc.addFunction(printMousePos)

    @staticmethod
    def __loadUnittests():
        params = UnittestManager.getParams()

        for test_unit, test_action_param_list in params.items():
            # print 'DBG test_unit', test_unit

            test_actions = []
            SystemUnittest.s_test_action_units[test_unit] = test_actions

            for index, test_param in enumerate(test_action_param_list):
                # print 'DBG index, test_param', index, test_param.test_action, test_param.test_action_params
                # print 'loadUnittest try find next test action:', test_param.test_action
                test_action_cls = TEST_ACTION_MAP.get(test_param.test_action)
                if test_action_cls is None:
                    # print 'cls "{}" not founded'.format(test_action_cls)
                    continue

                # print 'cls founded: ', test_action_cls
                test_action = test_action_cls(index, test_param)
                test_actions.append(test_action)

    def __runUnittests(self):
        delay_between_tests = UnittestManager.getDelayBetweenTests()
        delay_between_units = UnittestManager.getDelayBetweenUnits()

        run_unit_key_name = UnittestManager.s_run_unit_vk
        run_unit_key_code = UnittestManager.getRunUnitVK()

        skip_test_key_name = UnittestManager.s_skip_test_vk
        skip_test_key_code = UnittestManager.getSkipTestVK()

        time_all_units_start_holder = Holder()
        time_all_units_start_holder.set(Mengine.getTimeMs())
        time_unit_complete_holder = Holder()

        self.tc = TaskManager.createTaskChain(Name='Unittest', Repeat=False, Global=True)
        with self.tc as tc:
            tc.addPrint('[SystemUnittest] START UNIT TEST... WAIT FOR MENU SCREEN LOADED')
            tc.addListener(Notificator.onSceneEnter, Filter=lambda scene_name: scene_name == 'Menu')

            for unit_name, test_unit in SystemUnittest.s_test_action_units.iteritems():
                tc.addFunction(lambda: time_unit_complete_holder.set(Mengine.getTimeMs()))

                if run_unit_key_code is not None:
                    tc.addPrint('[SystemUnittest] PRESS {} BUTTON TO RUN UNITTEST {}'.format(run_unit_key_name, unit_name))
                    tc.addScope(self.__scopePressKey, run_unit_key_code)

                tc.addPrint('[SystemUnittest] UNIT TEST {} ARE RUNNING'.format(unit_name))

                if skip_test_key_code != -1:
                    tc.addPrint('[SystemUnittest] PRESS "{}" TO SKIP TEST'.format(skip_test_key_name))

                if delay_between_units != -1:
                    tc.addDelay(delay_between_units)

                with tc.addRaceTask(2) as (run_unit_source, interrupt_unit_source):
                    for test in test_unit:
                        with run_unit_source.addRaceTask(2) as (run_test, skip_test):
                            run_test.addScope(test.scopeAction)

                            if skip_test_key_code is not None:
                                skip_test.addDelay(1000)
                                skip_test.addScope(self.__scopePressKey, skip_test_key_code)
                                skip_test.addPrint('[SystemUnittest] "{}" PRESSED, TEST {} {} SKIPPED'.format(skip_test_key_name, test.param.test_action, test.param.test_action_params[0]))
                            else:
                                skip_test.addBlock()

                        if delay_between_tests != -1:
                            run_unit_source.addDelay(delay_between_tests)

                    if run_unit_key_code is not None:
                        interrupt_unit_source.addDelay(1000)
                        interrupt_unit_source.addPrint('[SystemUnittest] PRESS "{}" TO INTERRUPT UNIT'.format(run_unit_key_name))
                        interrupt_unit_source.addScope(self.__scopePressKey, run_unit_key_code)
                        interrupt_unit_source.addPrint('[SystemUnittest] "{}" PRESSED, INTERRUPT UNIT'.format(run_unit_key_name))
                    else:
                        interrupt_unit_source.addBlock()

                tc.addFunction(self.__printTimestamp, '[SystemUnittest] COMPLETE IN --{} sec UNIT {}', time_unit_complete_holder.get, unit_name)

            tc.addFunction(self.__printTimestamp, '[SystemUnittest] ALL TESTS COMPLETE --{} sec', time_all_units_start_holder.get)