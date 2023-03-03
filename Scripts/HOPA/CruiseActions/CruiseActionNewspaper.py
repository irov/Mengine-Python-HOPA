from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager


class CruiseActionNewspaper(CruiseAction, MixinObject):
    def _onParams(self, params):
        super(CruiseActionNewspaper, self)._onParams(params)
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionNewspaper')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionNewspaper')

    def _getCruiseObject(self):
        return self.Object

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()

        if Object.getType() == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()
        else:
            CruisePoint = Object.calcWorldHintPoint()
            if CruisePoint is not None:
                return CruisePoint
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()

        return Position

    def _onCheck(self):
        return True

    def _onAction(self):
        PositionTo = self._getCruisePosition(self.Object)
        if TaskManager.existTaskChain("CruiseActionNewspaper") is True:
            TaskManager.cancelTaskChain("CruiseActionNewspaper")

        with TaskManager.createTaskChain(Name="CruiseActionNewspaper") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.Object)
            tc.addTask("TaskDelay", Time=self.click_delay)
            tc.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.Object)
            tc.addTask("TaskDelay", Time=self.move_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
