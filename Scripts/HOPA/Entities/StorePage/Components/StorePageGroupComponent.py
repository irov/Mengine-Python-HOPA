from Foundation.MonetizationManager import MonetizationManager
from Foundation.SystemManager import SystemManager
from HOPA.Entities.StorePage.Components.StorePageBaseComponent import StorePageBaseComponent
from HOPA.System.SystemProductGroups import SystemProductGroups

class StorePageGroupComponent(StorePageBaseComponent):

    def __init__(self, page, group_id):
        super(StorePageGroupComponent, self).__init__(page)

        self.group_id = group_id
        self.group_params = None
        self.current_subgroup = None

        self.prod_buttons = {}  # { prod_id: button, ...}

    def _run(self):
        self._prepareButtons()

        if self._hasGroupDoubleBonus():
            self.handleBonusTag()

        if SystemProductGroups.hasGroup(self.group_id) is False:
            Trace.log("Entity", 1, "StorePageGroupComponent not found params for group {}".format(self.group_id))
            return

        self.handleGroupProducts()

    def _cleanUp(self):
        self.group_params = None
        self.current_subgroup = None
        self.prod_buttons = None

    # --- preparation --------------------------------------------------------------------------------------------------

    def _prepareButtons(self):
        for button in self.page.buttons:
            group_id = button.product_params.group_id
            prod_id = button.product_params.id

            if group_id != self.group_id:
                continue

            self.prod_buttons[prod_id] = button

    def _hasGroupDoubleBonus(self):
        return self.group_id in MonetizationManager.getGeneralSetting("DoubledGroupOnFirstPurchase", [])

    # --- bonus tag ----------------------------------------------------------------------------------------------------

    def handleBonusTag(self):
        if SystemManager.hasSystem("SystemMonetization") is False:
            Trace.log("Entity", 0, "StorePageGroupComponent handleBonusTag can't run: SystemMonetization is no active")
            return

        SystemMonetization = SystemManager.getSystem("SystemMonetization")
        if SystemMonetization.isProductGroupPurchased(self.group_id) is True:
            self._removeAllBonusTags()
            return

        self.addObserver(Notificator.onPaySuccess, self._cbPaySuccess)

    def _removeAllBonusTags(self):
        bonus_tag_name = "BonusTag"

        def _checkSubMovie(movie):
            return movie.entity.hasSubMovie(bonus_tag_name)

        for button in self.prod_buttons.values():
            for movie in button.movie.eachMovies():
                if _checkSubMovie(movie) is False:
                    # state has no such submovie
                    continue

                disable_layers = movie.getParam("DisableSubMovies")
                if bonus_tag_name in disable_layers:
                    # already disabled
                    continue

                movie.appendParam("DisableSubMovies", bonus_tag_name)

    # observers

    def _cbPaySuccess(self, prod_id):
        if prod_id not in self.prod_buttons:
            return False

        self._removeAllBonusTags()
        return True

    # --- group limit --------------------------------------------------------------------------------------------------

    def handleGroupProducts(self):
        SystemProductGroups.updateGroupsLimit()

        self.group_params = SystemProductGroups.getGroup(self.group_id)

        if self.group_params.in_progress is True:
            self.current_subgroup = SystemProductGroups.getActiveSubgroup(self.group_id)
            for purchased_product_id in self.current_subgroup.purchased:
                button = self._getProductButton(purchased_product_id)
                button.setBlock(True)
            self._blockOtherSubgroups()

        self.addObserver(Notificator.onProductGroupStartProgress, self._cbGroupStart)
        self.addObserver(Notificator.onProductGroupProgress, self._cbGroupProgress)
        self.addObserver(Notificator.onProductGroupReset, self._cbGroupReset)

    def _blockOtherSubgroups(self):
        other_subgroups = self.group_params.subgroups.copy()
        other_subgroups.pop(self.current_subgroup.id)

        for subgroup in other_subgroups.values():
            for product_id in subgroup.product_ids:
                self._setProgress(product_id)

    def _unblockAllButtons(self):
        for button in self.prod_buttons.values():
            button.setBlock(False)

    def _getProductButton(self, product_id):
        if product_id not in self.prod_buttons:
            Trace.log("Entity", 0, "StorePageGroupComponent [{}] not found button for product id '{}'".format(self.group_id, product_id))
            return
        button = self.prod_buttons[product_id]
        return button

    def _setProgress(self, product_id):
        button = self._getProductButton(product_id)
        button.setBlock(True)

    # observers

    def _cbGroupStart(self, group_id):
        if group_id != self.group_id:
            return False
        self.current_subgroup = SystemProductGroups.getActiveSubgroup(self.group_id)
        self._blockOtherSubgroups()
        return False

    def _cbGroupProgress(self, group_id, subgroup_id, product_id):
        if group_id != self.group_id:
            return False
        if subgroup_id != self.current_subgroup.id:
            return False

        self._setProgress(product_id)
        return False

    def _cbGroupReset(self, group_id):
        if group_id != self.group_id:
            return False
        self._unblockAllButtons()
        return False