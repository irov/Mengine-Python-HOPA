from Foundation.DefaultManager import DefaultManager
from Foundation.GroupManager import GroupManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.ZoomManager import ZoomManager

class SystemDebugPlayMovie(System):

    def __init__(self):
        super(SystemDebugPlayMovie, self).__init__()

        self.Handler = None

        self.Use = False
        pass

    def _onRun(self):
        super(SystemDebugPlayMovie, self)._onRun()
        self.Handler = Mengine.addKeyHandler(self.__onGlobalHandleKeyEvent)

        return True
        pass

    def __onGlobalHandleKeyEvent(self, event):
        if event.isDown is False:
            return
            pass

        if event.isRepeat is True:
            return
            pass

        if event.code != DefaultManager.getDefaultKey("DevDebugPlayMovie", "VK_CAPITAL"):
            return
            pass

        if SceneManager.isCurrentGameScene() is False:
            return
            pass

        if self.Use is True:
            return

        if SystemManager.hasSystem("SystemEditBox"):
            system_edit_box = SystemManager.getSystem("SystemEditBox")
            if system_edit_box.hasActiveEditbox():
                return

        self.playMovies()

        return
        pass

    def playMovies(self):
        zoomOpen = ZoomManager.getZoomOpen()
        if zoomOpen is None:
            return

        groupName = zoomOpen.getGroupName()

        group = GroupManager.getGroup(groupName)

        objects = group.getObjects()

        types = ["ObjectMovie", "ObjectMovie2"]

        for obj in objects:
            if obj.getEnable() is False:
                continue

            objType = obj.getType()

            if objType not in types:
                continue

            if obj.getPlay() is True:
                continue

            if objType is "ObjectMovie":
                TaskManager.runAlias("TaskMoviePlay", None, Movie=obj)
            elif objType is "ObjectMovie2":
                TaskManager.runAlias("TaskMovie2Play", None, Movie2=obj)

    def _onStop(self):
        super(SystemDebugPlayMovie, self)._onStop()
        Mengine.removeGlobalHandler(self.Handler)
        pass

    pass