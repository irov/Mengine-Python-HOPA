from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.TaskManager import TaskManager
from Foundation.Utils import getCurrentPublisher
from HOPA.Entities.Monetization.BaseComponent import BaseComponent


TC_NAME = "SpecialPackagePromotion"


class SpecialPackage(BaseComponent):
    """ one-time package (chapter+gold/energy) """

    _settings = {
        "is_enable": "EnablePromoPackage",
        "product_id": "PromoPackageProductID",
        "movie": "PromoPackageButtonName",
        "group": "PromoPackageGroupName",
    }
    _defaults = {
        "product_id": "-3",
        "movie": "Movie2Button_{}".format(getCurrentPublisher()),
        "group": "SpecialPackage",
    }

    def _createParams(self):
        self.demon_name = "SpecialPromotion"
        self.demon = DemonManager.getDemon(self.demon_name) if DemonManager.hasDemon(self.demon_name) else None
        self.button = None
        self.bonus_chapter_prod_id = MonetizationManager.getGeneralSetting("BonusChapterProductID")

    def _check(self):
        if self.group is None:
            self._error("Not found group {!r}".format(self.group_name))
            return False
        if self.group.hasObject(self.movie_name) is False:
            self._error("Not found movie {!r} in group {!r}".format(self.movie_name, self.group_name))
            return False
        if self.demon is None:
            self._error("Demon '{}' not found".format(self.demon_name))
            return False
        if self.product is None:
            self._error("Not found product {!r}".format(self._product_lookup_id))
            return False

        return True

    def _initialize(self):
        self.button = self.group.getObject(self.movie_name)
        return True

    def _run(self):
        if SystemMonetization.isProductPurchased(self.product.id):
            self._cbPackagePurchased()
            return True

        self.addObserver(Notificator.onStageInit, self._cbStageRun)
        self.addObserver(Notificator.onStageLoad, self._cbStageRun)
        return True

    def _cbPackagePurchased(self, isSkip=False):
        self.button.setEnable(False)

    def _cbStageRun(self, stage):
        if TaskManager.existTaskChain(TC_NAME):
            TaskManager.cancelTaskChain(TC_NAME)

        if SystemMonetization.isProductPurchased(self.product.id):
            self._cbPackagePurchased()
            return False

        self.button.setEnable(True)
        self.button.setInteractive(True)

        with TaskManager.createTaskChain(Name=TC_NAME, Cb=self._cbPackagePurchased) as tc:
            with tc.addRepeatTask() as (repeat, until):
                repeat.addTask("TaskMovie2ButtonClick", Group=self.group, Movie2Button=self.button)
                repeat.addFunction(self.demon.run, self.product.id)

                until.addListener(Notificator.onPaySuccess,
                                  Filter=lambda prod_id: prod_id in [self.product.id, self.bonus_chapter_prod_id])

        return False

    def _cleanUp(self):
        if TaskManager.existTaskChain(TC_NAME):
            TaskManager.cancelTaskChain(TC_NAME)
