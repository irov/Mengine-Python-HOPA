from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.Task import Task
from Foundation.TaskManager import TaskManager


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

    def _onFinally(self):
        super(TaskTipItemPlay, self)._onFinally()

        if self.Demon_TipItem is None:
            return

        # cancellation before the tip ended: the "TipItemPlay" chain keeps this task in its Cb
        if TaskManager.existTaskChain("TipItemPlay") is False:
            return

        TaskManager.cancelTaskChain("TipItemPlay")

        if self.Demon_TipItem.isActive() is False:
            return

        # the cancelled chain does not hide the tip any more
        self.Demon_TipItem.getObject("Text_Message").setEnable(False)
        Sprite_TipItem = self.Demon_TipItem.getObject("Sprite_TipItem")
        Sprite_TipItem.getEntity().getSprite().disable()

        Demon_TipEntity = self.Demon_TipItem.getEntity()
        Demon_TipEntity.releaseTip()
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
