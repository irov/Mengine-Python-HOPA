from Foundation.Task.Task import Task

from HOPA.FanManager import FanManager

class TaskFanPlay(Task):
    def _onParams(self, params):
        super(TaskFanPlay, self)._onParams(params)
        self.FanName = params.get("FanName")
        pass

    def _onInitialize(self):
        super(TaskFanPlay, self)._onInitialize()

        if _DEVELOPMENT is True:
            if FanManager.hasFan(self.FanName) is False:
                self.initializeFailed("TaskFanPlay: invalid FanName '%s'" % (self.HOGName))
                pass
            pass

        self.Fan = FanManager.getFanObject(self.FanName)
        pass

    def _onRun(self):
        if self.Fan.getPlay() is False:
            self.Fan.onPlay()
            pass

        return True
        pass
    pass