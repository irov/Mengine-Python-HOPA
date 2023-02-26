"""
Created on 14.08.2014 Up

@author: Me
"""
import Trace
from Foundation.Task.MixinTime import MixinTime
from Foundation.Task.Task import Task

class TaskDelayPointer(MixinTime, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskDelayPointer, self)._onParams(params)
        self.timePointer = params.get("TimePointer")
        self.id = 0
        pass

    def _onRun(self):
        self.time = self.timePointer[0]
        if (self.time <= 0):
            return True
        self.id = Mengine.schedule(self.time, self._onDelay)

        if self.id == 0:
            self.log("_onRun Mengine.schedule return 0 (%f)" % (self.time))
            return True
            pass

        return False
        pass

    def _onDelay(self, id, isRemoved):
        if self.id != id:
            return
            pass

        self.complete()
        pass

    def _onSkip(self):
        remove_id = self.id
        self.id = 0

        if Mengine.scheduleRemove(remove_id) is False:
            Trace.trace()
            pass
        pass
    pass