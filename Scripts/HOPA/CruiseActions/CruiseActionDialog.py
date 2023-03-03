from Foundation.Task.MixinGroup import MixinGroup
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction


class CruiseActionDialog(MixinGroup, CruiseAction):

    def _onInitialize(self):
        super(CruiseActionDialog, self)._onInitialize()
        pass

    def skip_Dialog(self):
        Notification.notify(Notificator.onKeyEvent, Mengine.KC_ESCAPE, 0, 0, True, False)
        Notification.notify(Notificator.onKeyEventEnd, Mengine.KC_ESCAPE, 0, 0, False, False)

    def _onAction(self):
        # demon = DemonManager.getDemon("Dialog")
        # button = demon.getObject("Movie2Button_Skip")
        # PositionTo = self._getCruisePosition(button)
        # if TaskManager.existTaskChain("CruiseActionDialog") is True:
        #     TaskManager.cancelTaskChain("CruiseActionDialog")
        #     pass

        with TaskManager.createTaskChain(Name="CruiseActionDialog") as tc:
            # tc.addTask("AliasCruiseControlAction", Position = PositionTo)
            tc.addFunction(self.skip_Dialog)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))
            pass
        pass

    # def _getCruisePosition(self, Object):
    #     name="socket"
    #     ObjectEntity = Object.getEntity()
    #     Movie=ObjectEntity.getCurrentMovie()
    #     Socket=Movie.getSocket(name)
    #     Position=Socket.getWorldPolygonCenter()
    #
    #     # CruisePoint = Object.calcWorldHintPoint()
    #     # if CruisePoint is not None:
    #     #     return CruisePoint
    #     #     pass
    #     # hotspot = ObjectEntity.getHotSpot()
    #     # Position = hotspot.getWorldPolygonCenter()
    #     return Position
    #     pass

    def _onEnd(self):
        super(CruiseActionDialog, self)._onEnd()
