from Foundation.DatabaseManager import DatabaseManager
from Foundation.GroupManager import GroupManager


class TabManager(object):

    @staticmethod
    def loadTabs(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            Name = record.get("Name")
            GroupName = record.get("GroupName")

            ModuleName = record.get("ModuleName")

            StartTab = record.get("StartTab")
            TabManager.addTab(Name, GroupName, module, ModuleName, StartTab)

    @staticmethod
    def addTab(Name, GroupName, module, param, StartTabName):
        records = DatabaseManager.getDatabaseRecords(module, param)

        tabs = {}

        for record in records:
            ButtonName = record.get("ButtonName")
            DemonName = record.get("DemonName")

            Demon = GroupManager.getObject(GroupName, DemonName)
            tabs[ButtonName] = Demon
            pass

        Tab = GroupManager.getObject(GroupName, Name)
        StartTab = GroupManager.getObject(GroupName, StartTabName)

        Tab.setTabs(tabs)
        Tab.setCurrentTab(StartTab)
