from Foundation.DatabaseManager import DatabaseManager
from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager

class SystemDebugHideInterface(System):
    INTERFACE_GROUPS = ["Inventory", "Hint", "Toolbar", "HintEffect", "OpenMap", "Navigation"]

    def __init__(self):
        super(SystemDebugHideInterface, self).__init__()

        self.Handler = None
        self.isInterfaceEnable = True

        self.Groups = []
        pass

    def _load_groups(self):
        self.Groups = []
        records = DatabaseManager.getDatabaseRecords("Database", "DebugHideInterfaceGroups")
        if records is None:
            self.Groups = self.INTERFACE_GROUPS
        else:
            for record in records:
                GroupName = record.get("GroupName")
                self.Groups.append(GroupName)

    def _onRun(self):
        super(SystemDebugHideInterface, self)._onRun()
        self._load_groups()

        self.Handler = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)

        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)

        return True
        pass

    def __onSceneInit(self, SceneName):
        self.isInterfaceEnable = True

        return False
        pass

    def __onGlobalHandleKeyEvent(self, event):
        if event.isDown is False:
            return
            pass

        if event.code != DefaultManager.getDefaultKey("DevDebugHideInterface", "VK_CAPITAL"):
            return None
            pass

        if SceneManager.isCurrentGameScene() is False:
            return None
            pass

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return None

        if self.isInterfaceEnable is True:
            self.enableInterface(False)
            self.isInterfaceEnable = False
            return None
            pass

        self.enableInterface(True)
        self.isInterfaceEnable = True

        return None
        pass

    def enableInterface(self, Value):
        for GroupName in self.Groups:
            if GroupManager.hasGroup(GroupName) is False:
                continue

            Group = GroupManager.getGroup(GroupName)
            if Value is True:
                Group.onEnable()
                pass
            else:
                Group.onDisable()
                pass
            pass
        pass

    pass