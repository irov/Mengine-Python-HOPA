from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.MindManager import MindManager


class TaskMindPlay(MixinObserver, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskMindPlay, self)._onParams(params)
        self.MindID = params.get("MindID")
        self.isZoom = params.get("isZoom", False)
        self.Static = params.get("Static")


    def _onInitialize(self):
        super(TaskMindPlay, self)._onInitialize()

        if _DEVELOPMENT is True:
            if MindManager.hasMind(self.MindID) is False:
                self.initializeFailed("MindID %s not found" % (self.MindID))

    def _onRun(self):
        self.addObserverFilter(Notificator.onMindPlayComplete, self._onMindShowComplete, self.MindID)

        MindManager.mindShow(self.MindID, self.isZoom, self.Static)

        return True

    def _onMindShowComplete(self, mindID, mindDemon):
        if self.MindID != mindID:
            return False

        return True
