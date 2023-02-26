from Foundation.DefaultManager import DefaultManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager

class SystemDebugNoGameArea(System):
    def __init__(self):
        super(SystemDebugNoGameArea, self).__init__()
        self.onButtonPressObserver = None
        self.onSceneInit = None
        self.isShowable = False
        self.Handler = None
        pass

    def _onRun(self):
        super(SystemDebugNoGameArea, self)._onRun()
        self.Handler = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)

        self.addObserver(Notificator.onSceneInit, self.__onSceneInit)

        return True
        pass

    def __onSceneInit(self, sceneName):
        if self.isShowable is True:
            self.beginDebugShow()
            return False
            pass

        self.endDebugShow()
        return False
        pass

    def __onGlobalHandleKeyEvent(self, event):
        if event.isDown is False:
            return
            pass

        if event.code != DefaultManager.getDefaultKey("DevDebugNoGameAreaShow", "VK_CONTROL"):
            return None
            pass

        if SceneManager.hasLayerScene("NoGameArea") is False:
            return None
            pass

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return None

        if self.isShowable is False:
            self.beginDebugShow()
            self.isShowable = True
            return None
            pass

        self.endDebugShow()
        self.isShowable = False

        return None
        pass

    def beginDebugShow(self):
        if SceneManager.hasLayerScene("NoGameArea") is False:
            return
            pass
        TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName="NoGameArea", Value=True)
        pass

    def endDebugShow(self):
        if SceneManager.hasLayerScene("NoGameArea") is False:
            return
            pass
        TaskManager.runAlias("TaskSceneLayerGroupEnable", None, LayerName="NoGameArea", Value=False)
        pass

    def _onStop(self):
        super(SystemDebugNoGameArea, self)._onStop()

        Mengine.removeGlobalHandler(self.Handler)
        pass

    pass