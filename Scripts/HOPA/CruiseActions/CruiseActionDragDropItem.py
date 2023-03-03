from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.MixinObjectTemplate import MixinItem
from Foundation.TaskManager import TaskManager

from HOPA.CruiseAction import CruiseAction


class CruiseActionDragDropItem(MixinItem, MixinObject, CruiseAction):

    def _onCheck(self):
        BlockInteractive = self.Item.getParam("BlockInteractive")
        if BlockInteractive is True:
            return False

        Enable = self.Item.getParam("Enable")
        if Enable is False:
            return False

        return True

    def _onAction(self):
        if self.Item.hasParam("HintPoint") and self.Object.hasParam("HintPoint"):
            Pos = self.Item.calcWorldHintPoint()
            Pos2 = self.Object.calcWorldHintPoint()

        else:
            if not self.Item.hasParam("HintPoint"):
                Trace.log("CruiseAction", 0, "CruiseActionDragDropItem can't calculate hint pos for ItemName %s, "
                                             "ItemType %s not supported" % (self.Item.getName(), self.Item.getType()))

            if not self.Object.hasParam("HintPoint"):
                Trace.log("CruiseAction", 0, "CruiseActionDragDropItem can't calculate hint pos for ItemName %s, "
                                             "ItemType %s not supported" % (self.Object.getName(), self.Object.getType()))

            Pos = (0.0, 0.0, 0.0)
            Pos2 = (0.0, 0.0, 0.0)

        if TaskManager.existTaskChain("CruiseActionDragDropItem") is True:
            TaskManager.cancelTaskChain("CruiseActionDragDropItem")

        with TaskManager.createTaskChain(Name="CruiseActionDragDropItem") as tc:
            tc.addTask("AliasCruiseControlAction", Position=Pos, Object=self.Item)
            tc.addTask("AliasCruiseControlAction", Position=Pos2, Object=self.Object)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionDragDropItem") is True:
            TaskManager.cancelTaskChain("CruiseActionDragDropItem")
