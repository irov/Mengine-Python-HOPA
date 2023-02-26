import Keys
from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class TestActionParam(object):
    def __init__(self, test_action, test_action_params):
        self.test_action = test_action
        self.test_action_params = test_action_params

class UnittestManager(Manager):
    s_unittest = {}

    s_delay_between_tests = -1
    s_delay_between_units = -1
    s_run_unit_vk = -1
    s_print_mouse_pos_vk = -1
    s_skip_test_vk = -1

    @staticmethod
    def loadParams(module, param):
        record = DatabaseManager.getDatabaseRecords(module, param)[0]
        '''
        DelayBetweenTests   DelayBetweenUnits   RunUnitVK   SkipTestVK	PrintMousePosVK TestQueueXlsx
        '''
        UnittestManager.s_delay_between_tests = record.get('DelayBetweenTests', -1)
        UnittestManager.s_delay_between_units = record.get('DelayBetweenUnits', -1)
        UnittestManager.s_run_unit_vk = record.get('RunUnitVK', -1)
        UnittestManager.s_skip_test_vk = record.get('SkipTestVK', -1)
        UnittestManager.s_print_mouse_pos_vk = record.get('PrintMousePosVK', -1)
        test_queue_xlsx = record.get('TestQueueXlsx')

        records = DatabaseManager.getDatabaseRecords(module, test_queue_xlsx)
        for record in records:
            '''
            TestXlsxName
            '''
            test_xlsx_name = record.get('TestXlsxName')

            result = UnittestManager.addParam(module, test_xlsx_name)
            if result is False:
                error_msg = "UnittestManager invalid addParam {}".format(module, test_xlsx_name)
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(module, test_xlsx_name):
        if test_xlsx_name in UnittestManager.s_unittest:
            error_msg = "UnittestManager already have test_param for {}".format(test_xlsx_name)
            Trace.log("Manager", 0, error_msg)
            return False

        records = DatabaseManager.getDatabaseRecords(module, test_xlsx_name)
        if records is None:
            error_msg = "UnittestManager cant find test_param database for {}".format(test_xlsx_name)
            Trace.log("Manager", 0, error_msg)
            return False

        UnittestManager.s_unittest[test_xlsx_name] = list()

        for record in records:
            '''
            TestAction	[TestActionParams]
            '''
            test_action = record.get('TestAction')
            test_action_params = record.get('TestActionParams', [None, -1, -1, -1])

            test_action_param = TestActionParam(test_action, test_action_params)

            UnittestManager.s_unittest[test_xlsx_name].append(test_action_param)

    @staticmethod
    def getDelayBetweenTests():
        return UnittestManager.s_delay_between_tests

    @staticmethod
    def getDelayBetweenUnits():
        return UnittestManager.s_delay_between_units

    @staticmethod
    def getRunUnitVK():
        return Keys.getVirtualKeyCode(UnittestManager.s_run_unit_vk)

    @staticmethod
    def getPrintMousePosVK():
        return Keys.getVirtualKeyCode(UnittestManager.s_print_mouse_pos_vk)

    @staticmethod
    def getSkipTestVK():
        return Keys.getVirtualKeyCode(UnittestManager.s_skip_test_vk)

    @staticmethod
    def getParam(test_xlsx_name):
        return UnittestManager.s_unittest.get(test_xlsx_name)

    @staticmethod
    def getParams():
        return UnittestManager.s_unittest