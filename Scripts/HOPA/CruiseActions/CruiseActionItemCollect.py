from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject
from Foundation.TaskManager import TaskManager

from HOPA.CruiseAction import CruiseAction
from HOPA.System.SystemItemCollect import SystemItemCollect


class CruiseActionItemCollect(MixinObject, CruiseAction):
    def _onParams(self, params):
        super(CruiseActionItemCollect, self)._onParams(params)
        self.ItemList = params.get('ItemList')

    def _onCheck(self):
        Demon = DemonManager.getDemon('ItemCollect')
        if Demon.isActive() is False:
            return False

        if Demon.getEnable() is False:
            return False

        if SystemItemCollect.s_CurrentOpenItemCollect is None:
            return False

        if SystemItemCollect.s_CurrentOpenItemCollect != (self.SceneName, self.Object.getName()):
            return False

        return True

    def _onAction(self):
        for itemName in self.ItemList:
            if not SystemItemCollect.hasFoundItem(itemName):
                # check for first item that not been placed yet

                IC_Param = SystemItemCollect.getItemCollect(itemName)

                with TaskManager.createTaskChain(Name="CruiseActionItemCollect") as tc:
                    tc.addTask("AliasCruiseControlAction",
                               Position=IC_Param.Item.calcWorldHintPoint(), Object=IC_Param.Item)
                    tc.addTask("AliasCruiseControlAction", Position=IC_Param.ItemPosition, Object=IC_Param.Silhouette)
                    tc.addNotify(Notificator.onCruiseActionEnd, self)

                return

    def _onEnd(self):
        if TaskManager.existTaskChain("CruiseActionItemCollect") is True:
            TaskManager.cancelTaskChain("CruiseActionItemCollect")
