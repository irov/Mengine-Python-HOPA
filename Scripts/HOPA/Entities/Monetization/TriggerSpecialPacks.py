from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.PolicyManager import PolicyManager
from HOPA.Entities.Monetization.BaseComponent import BaseComponent


class TriggerSpecialPacks(BaseComponent):
    _settings = {
        "scene_name": "TriggerSpecialPacksScene",
        "packs_order": "TriggerSpecialPacksOrder",
        "on_not_enough": "TriggerSpecialPacksOnNotEnough",
        "is_enable": "TriggerSpecialPacksEnable",
    }
    _defaults = {
        "is_enable": False,
        "on_not_enough": False,
    }

    def _createParams(self):
        self.scene_name = self._getMonetizationParam("scene_name")
        self.show_on_not_enough = self._getMonetizationParam("on_not_enough")
        packs = self._getMonetizationParam("packs_order", [])
        self.packs = [MonetizationManager.getProductRealId(product_id) for product_id in packs]
        self.index = 0
        self.demon_name = "SpecialPromotion"
        self.demon = DemonManager.getDemon(self.demon_name) if DemonManager.hasDemon(self.demon_name) else None

    def _check(self):
        if self.scene_name is None:
            self._error("Please setup scene for param `TriggerSpecialPacksScene`")
            return False
        if len(self.packs) == 0:
            self._error("Zero packs to show, check your `TriggerSpecialPacksOrder` param")
            return False
        if self.demon is None:
            self._error("Not found demon '{}'".format(self.demon_name))
            return False
        if _DEVELOPMENT is True:
            for product_id in self.packs:
                missing = []
                if MonetizationManager.getSpecialPromoById(product_id) is None:
                    missing.append(product_id)
                if len(missing) > 0:
                    self._error("Not found special promotions for product ids {}!!!!!!".format(missing))
                    return False
        return True

    def _run(self):
        self.addObserver(Notificator.onSceneActivate, self._cbSceneActivate)
        if self.show_on_not_enough is True:
            PolicyManager.setPolicy("NotEnoughGoldSecondAction", "PolicyNotEnoughGoldSpecialPacks")
            PolicyManager.setPolicy("NotEnoughEnergySecondAction", "PolicyNotEnoughEnergySpecialPacks")
        return True

    def _cbSceneActivate(self, scene_name):
        if scene_name is not self.scene_name:
            return False
        self.showPack()
        return False

    def getPackProductId(self):
        show_product_id = self.packs[self.index]
        return show_product_id

    def showPack(self):
        show_product_id = self.getPackProductId()
        self._nextIndex()
        self.demon.run(show_product_id)

    def _nextIndex(self):
        new_index = (self.index + 1) % len(self.packs)
        self.index = new_index

    def _save(self):
        return {"index": self.index}

    def _load(self, save):
        index = save.get("index", 0)
        if index > len(self.packs):
            self._error("save index {} > packs len {}".index(index, len(self.packs)))
            index = 0       # adjust
        self.index = index

