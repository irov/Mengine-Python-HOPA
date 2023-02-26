from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.MixinObjectTemplate import MixinItem

from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget
from HOPA.HintManager import HintManager

class HintActionDragDropItem(MixinItem, MixinObject, HintActionMultiTarget):

    def _getHintObject(self):
        return self.Object

    def _onCheck(self):
        if HintManager.inBlackList(self.Item) is True:
            return False

        BlockInteractive = self.Item.getParam("BlockInteractive")
        if BlockInteractive is True:
            return False

        Enable = self.Item.getParam("Enable")
        if Enable is False:
            return False

        return True

    def _getHintDoublePosition(self, hint):
        if self.Item.hasParam("HintPoint") and self.Object.hasParam("HintPoint"):
            Pos = self.Item.calcWorldHintPoint()
            Pos2 = self.Object.calcWorldHintPoint()

            if Pos is not None and Pos2 is not None:
                return Pos, Pos2

        Trace.log("HintAction", 0, "HintActionDragDropItem %s ItemType %s or ItemName %s ItemType %s "
                                   "cant calculate position" % (self.Item.name, self.Item.getType(), self.Object.name, self.Object.getType()))

        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)

    def _onAction(self, hint):
        points = self.getHintDoublePosition(hint)
        self.showHint(*points)