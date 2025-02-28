from HOPA.CruiseAction import CruiseAction
from Foundation.Task.MixinObject import MixinObject
from HOPA.ElementalMagicManager import ElementalMagicManager
from Foundation.TaskManager import TaskManager


class CruiseActionElementalMagicUse(CruiseAction, MixinObject):
    def _onParams(self, params):
        super(CruiseActionElementalMagicUse, self)._onParams(params)

        self.Ring = ElementalMagicManager.getMagicRing()
        self.Element = params["Element"]

    def _getCruiseObject(self):
        return self.Object

    def _onCheck(self):
        if ElementalMagicManager.getPlayerElement() == self.Element:
            return True
        return False

    def _onAction(self):
        self.showCruise()

    def showCruise(self):
        Pos1, Pos2 = self.getMultiTargetPosition()

        if TaskManager.existTaskChain("CruiseActionElementalMagicUse"):
            TaskManager.cancelTaskChain("CruiseActionElementalMagicUse")

        with TaskManager.createTaskChain(Name="CruiseActionElementalMagicUse") as tc:
            tc.addTask("AliasCruiseControlAction", Position=Pos1, Object=self.Ring.getRootNode())

            if Pos2 is not None:
                tc.addTask("AliasCruiseControlAction", Position=Pos2, Object=self.Object)

            tc.addNotify(Notificator.onCruiseActionEnd, self)

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

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionElementalMagicUse"):
            TaskManager.cancelTaskChain("CruiseActionElementalMagicUse")
