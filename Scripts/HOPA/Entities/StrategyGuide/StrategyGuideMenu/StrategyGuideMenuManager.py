from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager

class StrategyGuideMenuManager(Manager):
    s_buttons = {}

    @staticmethod
    def _onFinalize():
        StrategyGuideMenuManager.s_buttons = {}
        pass

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            pageId = record.get("GuidePageID")
            GroupName = record.get("GroupName")
            ButtonName = record.get("ButtonName")

            button = GroupManager.getObject(GroupName, ButtonName)

            StrategyGuideMenuManager.s_buttons[button] = pageId
            pass
        pass

    @staticmethod
    def getButtons():
        return StrategyGuideMenuManager.s_buttons