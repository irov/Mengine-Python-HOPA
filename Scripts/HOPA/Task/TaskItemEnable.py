"""
Created on 13.09.2011

@author: Me
"""
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.Task.Task import Task

class TaskItemEnable(MixinItem, Task):
    def _onParams(self, params):
        super(TaskItemEnable, self)._onParams(params)
        pass

    def _onRun(self):
        self.Item.setEnable(True)
        return True
        pass
    pass