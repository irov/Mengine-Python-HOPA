"""
Created on 07.10.2011
@author: Me
"""

from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.Task import Task

class TaskTipItemPlay(MixinGroup, Task):
    def _onParams(self, params):
        super(TaskTipItemPlay, self)._onParams(params)

        self.fadeTo = params.get("To", 1)
        self.TipItemID = params.get("TipItemID")
        self.Demon_TipItem = None
        self.delayTime = params.get("DelayTime")
        pass

    def _onInitialize(self):
        super(TaskTipItemPlay, self)._onInitialize()
        pass

    def _onRun(self):
        self.Demon_TipItem = self.Group.getObject("Demon_TipItem")
        Demon_TipEntity = self.Demon_TipItem.getEntity()
        Demon_TipEntity.tipShow(self.TipItemID, self.delayTime, self._onTipShowComplete)

        return False
        pass

    def _onTipShowComplete(self, tip):
        if tip is not self.Demon_TipItem:
            return False
            pass

        self.complete()
        return True
        pass

    def _onSkip(self):
        Demon_TipEntity = self.Demon_TipItem.getEntity()
        Demon_TipEntity.releaseTip()
        pass

    def isSkip(self):
        Demon_TipEntity = self.Demon_TipItem.getEntity()
        Demon_TipEntity.releaseTip()
        pass

    pass