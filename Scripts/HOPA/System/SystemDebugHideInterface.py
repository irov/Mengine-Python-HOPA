from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager


class SystemDebugHideInterface(System):
    DEFAULT_INTERFACE_GROUPS = ["Inventory", "Hint", "Toolbar", "HintEffect", "OpenMap", "Navigation"]

    def __init__(self):
        super(SystemDebugHideInterface, self).__init__()
        self.handler = None
        self.interface_state = True
        self.groups = []

    def _load_groups(self):
        records = DatabaseManager.getDatabaseRecords("Database", "DebugHideInterfaceGroups")

        if records is None:
            self.groups = self.DEFAULT_INTERFACE_GROUPS
            return

        for record in records:
            group_name = record.get("GroupName")
            self.groups.append(group_name)

    def _onRun(self):
        super(SystemDebugHideInterface, self)._onRun()
        self._load_groups()
        self.handler = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)
        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)
        return True

    def __onSceneInit(self, SceneName):
        self.interface_state = True
        return False

    def __onGlobalHandleKeyEvent(self, event):
        if event.isDown is False:
            return

        if event.code != DefaultManager.getDefaultKey("DevDebugHideInterface", "VK_CAPITAL"):
            return None

        if SceneManager.isCurrentGameScene() is False:
            return None

        if SystemManager.hasSystem("SystemEditBox") is True:
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return None

        if isinstance(self.getInterfaceState(), bool) is True:
            self.switchInterfaceStateTo(not self.getInterfaceState())

        return None

    def switchInterfaceStateTo(self, state):
        for group_name in self.groups:
            if GroupManager.hasGroup(group_name) is False:
                continue

            group = GroupManager.getGroup(group_name)

            if group.isActive() is False:
                continue

            if state is True:
                if group.getEnable() is False:
                    group.onEnable()
            else:
                if group.getEnable() is True:
                    group.onDisable()

        self.interface_state = state

    def getInterfaceState(self):
        return self.interface_state
