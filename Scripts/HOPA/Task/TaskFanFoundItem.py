"""
Created on 13.09.2011

@author: Me
"""
from Foundation.Task.MixinObjectTemplate import MixinFan
from Foundation.Task.Task import Task

class TaskFanFoundItem(MixinFan, Task):
    def _onParams(self, params):
        super(TaskFanFoundItem, self)._onParams(params)
        self.ItemName = params.get("ItemName")
        pass

    def _onInitialize(self):
        super(TaskFanFoundItem, self)._onInitialize()

        if _DEVELOPMENT is True:
            FindItems = self.Fan.getParam("FindItems")

            if self.ItemName not in FindItems:
                self.initializeFailed("Item %s not found in FindItems %s" % (self.ItemName, FindItems))
                pass
            pass

        # FoundItems = self.Fan.getParam("FoundItems")

        # if self.ItemName in FoundItems:
        #     self.initializeFailed("Item %s already in FoundItems %s"%(self.ItemName, FoundItems))
        #     pass
        pass

    def _onRun(self):
        self.Fan.appendParam("FoundItems", self.ItemName)
        return True
        pass