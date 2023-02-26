from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction

class CruiseActionSpellUse(CruiseAction):
    def __init__(self):
        super(CruiseActionSpellUse, self).__init__()
        pass

    def _onParams(self, params):
        super(CruiseActionSpellUse, self)._onParams(params)
        self.Spell = params.get("Spell")
        self.Object = params.get("Object")
        pass

    def _getCruiseObject(self):
        return self.Spell
        pass

    def _getCruisePosition(self, Object):
        ObjectEntity = Object.getEntity()
        Socket = ObjectEntity.getSocket()
        SocketEntity = Socket.getEntity()
        hotspot = SocketEntity.getHotSpot()
        Position = hotspot.getWorldPolygonCenter()
        return Position
        pass

    def _onCheck(self):
        State = self.Spell.getParam("CurrentState")
        if State != "Ready":
            return False
            pass
        pass
        return True

    def _onAction(self):
        self.showCruise()
        pass

    def showCruise(self):
        hObject = self._getCruiseObject()
        PositionTo1 = self._getCruisePosition(hObject)

        PlaceObjectType = self.Object.getType()

        if PlaceObjectType == "ObjectItem":
            ItemEntity = self.Object.getEntity()
            Sprite = ItemEntity.getSprite()

            PositionTo2 = Sprite.getWorldImageCenter()
            pass

        else:
            cruisePoint = self.Object.calcWorldHintPoint()
            if cruisePoint is not None:
                PositionTo2 = cruisePoint
                pass
            else:
                ObjectEntity = self.Object.getEntity()
                HotSpot = ObjectEntity.getHotSpot()

                PositionTo2 = HotSpot.getWorldPolygonCenter()
                pass
            pass

        if TaskManager.existTaskChain("CruiseActionSpellUse") is True:
            TaskManager.cancelTaskChain("CruiseActionSpellUse")
            pass

        with TaskManager.createTaskChain(Name="CruiseActionSpellUse") as tc:
            tc.addTask("AliasCruiseControlAction", Position=PositionTo1)
            tc.addTask("TaskDelay", Time=0.5 * 1000)  # speed fix
            tc.addTask("AliasCruiseControlAction", Position=PositionTo2)
            tc.addTask("TaskDelay", Time=0.5 * 1000)  # speed fix
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
        pass

    def _onEnd(self):
        super(CruiseActionSpellUse, self)._onEnd()
        pass
    pass