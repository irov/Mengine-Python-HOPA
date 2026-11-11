from HOPA.CruiseAction import CruiseAction
from Foundation.Task.MixinObject import MixinObject
from HOPA.ElementalMagicManager import ElementalMagicManager


class CruiseActionElementalMagicPick(CruiseAction, MixinObject):
    def _onParams(self, params):
        super(CruiseActionElementalMagicPick, self)._onParams(params)

        self.Ring = ElementalMagicManager.getMagicRing()
        self.Element = params["Element"]
        self.MagicId = params["MagicId"]

    def _getCruiseObject(self):
        return self.Object

    def _onCheck(self):
        if ElementalMagicManager.hasUseQuestOnElement(self.MagicId) is False:
            return False
        if ElementalMagicManager.getPlayerElement() is not None:
            return False

        # user should have use quest and be empty
        return True

    def _onAction(self, source):
        self.showCruise(source)

    def showCruise(self, source):
        Pos1, Pos2 = self.getMultiTargetPosition()

        source.addTask("AliasCruiseControlAction", Position=Pos1, Object=self.Ring.getRootNode())

        if Pos2 is not None:
            source.addTask("AliasCruiseControlAction", Position=Pos2, Object=self.Object)

        source.addNotify(Notificator.onCruiseActionEnd, self)

    def getMultiTargetPosition(self):
        Node = self.Ring.getRootNode()
        Pos1 = Node.getWorldPosition()

        if self.Object is None:
            Pos2 = None
            return Pos1, Pos2

        HintPoint = self.Object.calcWorldHintPoint()
        if HintPoint is not None:
            Pos2 = HintPoint
        else:
            ObjectEntity = self.Object.getEntity()
            HotSpot = ObjectEntity.getHotSpot()
            Pos2 = HotSpot.getWorldPolygonCenter()

        return Pos1, Pos2
