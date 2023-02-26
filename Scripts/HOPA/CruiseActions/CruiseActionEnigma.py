from Foundation.SystemManager import SystemManager
from Foundation.Task.MixinGroup import MixinGroup
from Foundation.TaskManager import TaskManager
from HOPA.CruiseAction import CruiseAction
from HOPA.CruiseControlManager import CruiseControlManager
from HOPA.EnigmaManager import EnigmaManager
from HOPA.Entities.HOGFitting.ObjectHOGFitting import ObjectHOGFitting
from HOPA.Object.ObjectHOG import ObjectHOG
from HOPA.Object.ObjectHOGRolling import ObjectHOGRolling

class CruiseActionEnigma(MixinGroup, CruiseAction):

    def _onParams(self, params):
        super(CruiseActionEnigma, self)._onParams(params)
        self.EnigmaName = params.get("EnigmaName")
        self.click_delay = CruiseControlManager.getCruiseClickDelay('CruiseActionEnigma')
        self.move_delay = CruiseControlManager.getCruiseMoveDelay('CruiseActionEnigma')

    def _onInitialize(self):
        super(CruiseActionEnigma, self)._onInitialize()

    def _onCheck(self):
        enigmaObject = EnigmaManager.getEnigmaObject(self.EnigmaName)
        if isinstance(enigmaObject, ObjectHOGRolling):
            return False

        if isinstance(enigmaObject, ObjectHOG):
            return False

        if isinstance(enigmaObject, ObjectHOGFitting):
            return False

        return True

    def _onAction(self):
        if TaskManager.existTaskChain("CruiseActionDefault") is True:
            TaskManager.cancelTaskChain("CruiseActionDefault")

        with TaskManager.createTaskChain(Name="CruiseActionDefault") as tc:
            tc.addTask("TaskDelay", Time=self.click_delay)
            tc.addTask("TaskNotify", ID=Notificator.onEnigmaSkip)
            tc.addTask("TaskDelay", Time=self.move_delay)
            tc.addTask("TaskNotify", ID=Notificator.onCruiseActionEnd, Args=(self,))

    def getHint_Position(self):
        SystemHint = SystemManager.getSystem("SystemHint")
        Hint = SystemHint.getHintObject()
        P0 = Hint.getPoint()
        return P0

    def _onEnd(self):
        super(CruiseActionEnigma, self)._onEnd()

        if TaskManager.existTaskChain("CruiseActionDefault") is True:
            TaskManager.cancelTaskChain("CruiseActionDefault")