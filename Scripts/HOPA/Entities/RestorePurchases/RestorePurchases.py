from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from Foundation.Providers.PaymentProvider import PaymentProvider

BUTTON_NAME = "Movie2Button_RestorePurchases"
EFFECT_NAME = "Movie2_EffectDone"


class RestorePurchases(BaseEntity):

    def __init__(self):
        super(RestorePurchases, self).__init__()
        self.button = None
        self.button_center = None
        self._active = False

    @staticmethod
    def callRestorePurchases():
        PaymentProvider.restorePurchases()

    def startAnimation(self):
        if self.object.hasObject(EFFECT_NAME) is False:
            return

        anim = self.object.getObject(EFFECT_NAME)
        anim.setEnable(True)

        anim_node = anim.getEntityNode()
        anim_node.setWorldPosition(self.button_center)

        tc = TaskManager.createTaskChain()
        with tc as tc:
            tc.addPlay(anim, Wait=True)
            tc.addDisable(anim)

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

        self.button_center = self.button.getCurrentMovieSocketCenter()

        with TaskManager.createTaskChain(Name="RestorePurchasesListener", Repeat=True) as tc:
            tc.addListener(Notificator.onRestorePurchasesDone)
            tc.addFunction(self.startAnimation)

        with TaskManager.createTaskChain(Name="RestorePurchasesButton", Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button)
            tc.addFunction(self.callRestorePurchases)

    def _onDeactivate(self):
        if TaskManager.existTaskChain("RestorePurchasesButton") is True:
            TaskManager.cancelTaskChain("RestorePurchasesButton")

        if TaskManager.existTaskChain("RestorePurchasesListener") is True:
            TaskManager.cancelTaskChain("RestorePurchasesListener")

        self.button = None
        self.button_center = None

    def _prepareEnable(self):
        is_monetization = MonetizationManager.isMonetizationEnable()
        is_mobile = Mengine.hasTouchpad() is True
        is_enable = Mengine.getConfigBool("Monetization", "RestorePurchases", False) is True
        self._active = is_monetization and is_mobile and is_enable

        return self._active
