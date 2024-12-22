from Foundation.System import System

from Foundation.MonetizationManager import MonetizationManager

class SystemRestorePurchases(System):
    OPEN_TRIGGERS = ["InGameMenu"]

    def _onRun(self):
        if MonetizationManager.isMonetizationEnable() is False:
            return True
            pass

        self.addObserver(Notificator.onLayerGroupEnable, self._cbLayerGroupEnable)
        self.addObserver(Notificator.onLayerGroupDisable, self._cbLayerGroupDisable)

        return True

    def _cbLayerGroupEnable(self, group_name):
        if group_name not in self.OPEN_TRIGGERS:
            return False

        if self.existTaskChain("SystemRestorePurchases_Disappear") is True:
            self.removeTaskChain("SystemRestorePurchases_Disappear")

        if self.existTaskChain("SystemRestorePurchases_Appear") is True:
            self.removeTaskChain("SystemRestorePurchases_Appear")
        with self.createTaskChain(Name="SystemRestorePurchases_Appear") as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="RestorePurchases", Value=True)

        return False

    def _cbLayerGroupDisable(self, group_name):
        if group_name not in self.OPEN_TRIGGERS:
            return False

        if self.existTaskChain("SystemRestorePurchases_Disappear") is True:
            self.removeTaskChain("SystemRestorePurchases_Disappear")
        with self.createTaskChain(Name="SystemRestorePurchases_Disappear", Repeat=False) as tc:
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="RestorePurchases", Value=False)

        return False
