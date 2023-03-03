from Foundation.GroupManager import GroupManager
from Foundation.Task.MixinObject import MixinObject
from HOPA.HintActions.HintActionDefault import HintActionDefault


class HintActionShiftCollect(HintActionDefault, MixinObject):
    def _onParams(self, params):
        super(HintActionShiftCollect, self)._onParams(params)

        self.Collects = params["Collects"]
        self.CollectIndex = params["CollectIndex"]

        self.Collect = self.Collects[self.CollectIndex]

        self.Object = GroupManager.getObject(self.GroupName, self.Collect["InteractionName"])

    def _onCheck(self):
        if len(self.Collects) == 0:
            return False

        if self.Object.isActive() is False:
            return False

        ShiftName = self.Collect["ShiftName"]
        Shift = self.Group.getObject(ShiftName)
        State = Shift.getShift()
        WaitState = self.Collect["State"]

        if State != WaitState:
            return True

        return False

    def _getHintObject(self):
        return self.Object

    def _getHintPosition(self, Object):
        if Object.hasParam("HintPoint"):
            HintPoint = Object.calcWorldHintPoint()

            if HintPoint is not None:
                return HintPoint

        return 0.0, 0.0, 0.0
