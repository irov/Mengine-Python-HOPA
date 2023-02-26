from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager

class CruiseActionNewspaper(CruiseAction, MixinObject):
    def _onParams(self, params):
        super(CruiseActionNewspaper, self)._onParams(params)
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionNewspaper')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionNewspaper')
        pass

    def _getCruiseObject(self):
        return self.Object
        pass

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()

        if Object.getType() == "ObjectItem":
            Sprite = ObjectEntity.getSprite()
            Position = Sprite.getWorldImageCenter()
            pass
        else:
            CruisePoint = Object.calcWorldHintPoint()
            if CruisePoint is not None:
                return CruisePoint
            hotspot = ObjectEntity.getHotSpot()
            Position = hotspot.getWorldPolygonCenter()
            pass

        return Position
        pass

    def _onCheck(self):
        return True
        pass

    def _onAction(self):
        PositionTo = self._getCruisePosition(self.Object)
        if TaskManager.existTaskChain("CruiseActionNewspaper") is True:
            TaskManager.cancelTaskChain("CruiseActionNewspaper")
            pass

        with TaskManager.createTaskChain(Name="CruiseActionNewspaper") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.Object)
            tc.addTask("TaskDelay", Time=self.click_delay)
            tc.addTask("AliasCruiseControlAction", Position=PositionTo, Object=self.Object)
            tc.addTask("TaskDelay", Time=self.move_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
            pass
        pass
    pass