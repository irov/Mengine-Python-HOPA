from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.Systems.SystemAppleServices import SystemAppleServices
from Foundation.Systems.SystemGoogleServices import SystemGoogleServices


class RestorePurchases(BaseEntity):

    @staticmethod
    def callRestorePurchases():
        if Utils.getCurrentPlatform() == "IOS":
            SystemAppleServices.restorePurchases()
        elif Utils.getCurrentPlatform() == "Android":
            SystemGoogleServices.restorePurchases()
        else:
            Trace.msg_err("Not found module to call Restore Purchases :'(")

    def _onPreparation(self):
        with TaskManager.createTaskChain(Name="RestorePurchasesButton", Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2ButtonName="Movie2Button_RestorePurchases")
            tc.addFunction(self.callRestorePurchases)

    def _onDeactivate(self):
        if TaskManager.existTaskChain("RestorePurchasesButton") is True:
            TaskManager.cancelTaskChain("RestorePurchasesButton")
