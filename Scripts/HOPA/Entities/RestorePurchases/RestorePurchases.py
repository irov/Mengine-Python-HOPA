from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.Systems.SystemAppleServices import SystemAppleServices
from Foundation.Systems.SystemGoogleServices import SystemGoogleServices

BUTTON_NAME = "Movie2Button_RestorePurchases"


class RestorePurchases(BaseEntity):

    def __init__(self):
        super(RestorePurchases, self).__init__()
        self.button = None

    @staticmethod
    def callRestorePurchases():
        if Utils.getCurrentPlatform() == "IOS":
            SystemAppleServices.restorePurchases()
        elif Utils.getCurrentPlatform() == "Android":
            SystemGoogleServices.restorePurchases()
        else:
            Trace.msg_err("Not found module to call Restore Purchases :'(")

    def _onPreparation(self):
        if self.object.hasObject(BUTTON_NAME) is False:
            Trace.log("Entity", 0, "Demon {} should has object {}".format(self.object.getName(), BUTTON_NAME))
            return

        self.button = self.object.getObject(BUTTON_NAME)

        with TaskManager.createTaskChain(Name="RestorePurchasesButton", Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button)
            tc.addFunction(self.callRestorePurchases)

    def _onDeactivate(self):
        if TaskManager.existTaskChain("RestorePurchasesButton") is True:
            TaskManager.cancelTaskChain("RestorePurchasesButton")

        self.button = None
