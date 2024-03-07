from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.Providers.AdvertisementProvider import AdvertisementProvider
from Foundation.DefaultManager import DefaultManager

BUTTON_NAME = DefaultManager.getDefault("ConsentFlowButtonName", "Movie2Button_ConsentFlow")


class ConsentFlow(BaseEntity):
    def __init__(self):
        super(ConsentFlow, self).__init__()
        self.button = None
        self.tc = None
        self._active = False

    def _onPreparation(self):
        if self.object.hasObject(BUTTON_NAME) is False:
            Trace.log("Entity", 0, "Demon {} should has object {}".format(self.object.getName(), BUTTON_NAME))
            return

        self.button = self.object.getObject(BUTTON_NAME)

        is_active = self._prepareEnable()
        self.button.setEnable(is_active)

    def _onActivate(self):
        if self.button is None or self._active is False:
            return

        self.tc = TaskManager.createTaskChain(Name="ConsentFlowButton", Repeat=True)
        with self.tc as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button)
            tc.addFunction(AdvertisementProvider.showConsentFlow)
            tc.addDelay(1000)  # anti-spam

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()

        self.button = None

    def _prepareEnable(self):
        self._active = AdvertisementProvider.isConsentFlow() is True
        return self._active

