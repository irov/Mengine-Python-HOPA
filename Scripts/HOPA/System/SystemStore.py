from Foundation.DemonManager import DemonManager
from Foundation.MonetizationManager import MonetizationManager
from Foundation.SceneManager import SceneManager
from Foundation.System import System
from Foundation.Systems.SystemAnalytics import SystemAnalytics
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.TaskManager import TaskManager
from HOPA.StoreManager import StoreManager
from Notification import Notification
from Foundation.Utils import SimpleLogger

_Log = SimpleLogger("SystemStore")


class SystemStore(System):

    def __init__(self):
        super(SystemStore, self).__init__()
        self.__prefetchedPages = []

    def _onRun(self):
        self._setupObservers()

        self._setupPageID()
        self._setupHiddenPagesID()
        self._setupUnvisitedPagesID()

        self._addAnalytics()

        return True

    def _onStop(self):
        self.__unfetchPages()

    # === Initial ======================================================================================================

    def _setupPageID(self):
        """ initial page for Store (reset page"""
        Store = DemonManager.getDemon("Store")

        tabs = StoreManager.getTabsSettings().values()
        selected_tabs = filter(lambda tab: tab.selected is True, tabs)
        if len(selected_tabs) == 0:
            return False
        page_id = selected_tabs[0].page_id  # StoreManager guarantees that at least one page is selected

        current_page_id = Store.getParam("CurrentPageID")
        if current_page_id == page_id or current_page_id is not None:
            return

        self.setCurrentPageID(page_id)

    def _setupAlreadyBoughtPagesID(self):
        """ Analyze every page hide trigger and hides page if product already purchased
            Page could be not hidden because these pages saves with all game
            If user bought something and immediately leave game - on next enter page will be shown
            This method fixes this bug :)
        """

        tab_params = StoreManager.getTabsSettings()
        for page_id, params in tab_params.items():
            if params.trigger_hide_product_id is None:
                continue

            # Do not forget to check real id, not alias !
            for trigger in params.trigger_hide_product_id:
                product = MonetizationManager.getProductInfo(trigger)
                
                if SystemMonetization.isProductPurchased(product.id) is True:
                    self.hidePageID(page_id)
                    break

    def _setupHiddenPagesID(self):
        Store = DemonManager.getDemon("Store")

        if Store.getParam("HiddenPagesID") is not None:
            # this param is already inited before
            return

        Store.setParam("HiddenPagesID", [])

        tabs = StoreManager.getTabsSettings().values()
        hidden_tabs = filter(lambda tab: tab.hidden is True, tabs)

        for tab in hidden_tabs:
            page_id = tab.page_id
            self.hidePageID(page_id)

    def _setupUnvisitedPagesID(self):
        Store = DemonManager.getDemon("Store")

        if Store.getParam("UnvisitedPagesID") is not None:
            # this param is already inited before
            return

        Store.setParam("UnvisitedPagesID", [])

        tabs = StoreManager.getTabsSettings().values()
        unvisited_tabs = filter(lambda tab: tab.first_visited is False, tabs)

        for tab in unvisited_tabs:
            page_id = tab.page_id
            self.addPageNotify(page_id)

    # === Page handler =================================================================================================

    @staticmethod
    def setCurrentPageID(page_id):
        """ changes current page id for store - it will be opened after Store init
            or switch page if you are in Store """
        Store = DemonManager.getDemon("Store")
        Store.setParam("CurrentPageID", page_id)

    @staticmethod
    def hidePageID(page_id):
        """ hide page - it won't be created after init Store or removed tab + switch page if you are in Store"""
        Store = DemonManager.getDemon("Store")
        pages = Store.getParam("HiddenPagesID")
        if pages is None:
            _Log("hidePageID {!r} fail - Store is not initialized".format(page_id), err=True)
            return
        if page_id in pages:
            return
        Store.appendParam("HiddenPagesID", page_id)

    @staticmethod
    def showPageID(page_id):
        """ show page, but user should re-enter to the Store """
        Store = DemonManager.getDemon("Store")
        pages = Store.getParam("HiddenPagesID")
        if pages is None:
            _Log("showPageID {!r} fail - Store is not initialized".format(page_id), err=True)
            return
        if page_id not in pages:
            return
        Store.delParam("HiddenPagesID", page_id)

    @staticmethod
    def addPageNotify(page_id):
        """ add red dot near page tab (notify that something interesting inside) """
        Store = DemonManager.getDemon("Store")
        pages = Store.getParam("UnvisitedPagesID")
        if pages is None:
            _Log("addPageNotify {!r} fail - Store is not initialized".format(page_id), err=True)
            return
        if page_id in pages:
            return
        Store.appendParam("UnvisitedPagesID", page_id)

    @staticmethod
    def removePageNotify(page_id):
        """ remove red dot near page tab """
        Store = DemonManager.getDemon("Store")
        pages = Store.getParam("UnvisitedPagesID")
        if pages is None:
            _Log("removePageNotify {!r} fail - Store is not initialized".format(page_id), err=True)
            return
        if page_id not in pages:
            return
        Store.delParam("UnvisitedPagesID", page_id)

    # === Observers ====================================================================================================

    def _addAnalytics(self):
        SystemAnalytics.addAnalytic(
            "store_open_page", Notificator.onStoreTabSwitched, service_key="screen_view",
            params_method=lambda _, to_page_id: {"screen_type": "MengineStorePage", "screen_name": to_page_id})
        SystemAnalytics.addAnalytic("store_click", Notificator.onStorePageButtonClick, params_method=lambda button: {
            "action": button.action,
            "product_id": button.product_params.id,
            "button_id": button.id,
        })

    def _setupObservers(self):
        tab_params = StoreManager.getTabsSettings()
        for page_id, params in tab_params.items():
            self.__createTabObserver(params)

        self.addObserver(Notificator.onStoreTabSectionClickedTab, self._onTabClicked)
        self.addObserver(Notificator.onStoreTabSectionClickedBack, self._onClickedBack)
        self.addObserver(Notificator.onStorePageNewActions, self._cbPageNewActions)
        self.addObserver(Notificator.onStorePageNewActionsEnd, self._cbPageNewActionsEnd)
        self.addObserver(Notificator.onStoreTabSwitched, self._onTabSwitched)
        self.addObserver(Notificator.onStoreSetPage, self._onStoreSetPage)
        self.addObserver(Notificator.onIndicatorClicked, self._cbIndicatorClicked)
        self.addObserver(Notificator.onAvailableAdsNew, self._cbAvailableAdsNew)
        self.addObserver(Notificator.onStageInit, self._cbStageInit)
        # prefetch pages
        self.addObserver(Notificator.onTransitionBegin, self._cbTransitionBegin)

    def _cbAvailableAdsNew(self, ad_name):
        advert_product = MonetizationManager.findProduct(lambda product: product.name == ad_name)
        if advert_product is None:
            _Log("_cbAvailableAdsNew: New available ads {!r}, but not found its product".format(ad_name), err=True)
            return False

        advert_page_id = StoreManager.findPageIdByProductId(advert_product.id)
        if advert_page_id is None:
            _Log("_cbAvailableAdsNew: New available ads {!r}, but not found page for it".format(ad_name), err=True)
            return False

        Notification.notify(Notificator.onStorePageNewActions, advert_page_id)
        return False

    def _cbPageNewActions(self, page_id):
        self.addPageNotify(page_id)
        return False

    def _cbPageNewActionsEnd(self, page_id):
        self.removePageNotify(page_id)
        return False

    def _cbIndicatorClicked(self, indicator_type):
        page_id = MonetizationManager.getGeneralSetting("%sPageID" % indicator_type)
        if page_id is not None:
            self.setCurrentPageID(page_id)
        Store = DemonManager.getDemon("Store")
        Store.open()
        return False

    def __createTabObserver(self, params):
        if params.trigger_hide_product_id is not None:
            def _cbPaySuccess(prod_id):
                product = MonetizationManager.getProductInfo(prod_id)

                for trigger in params.trigger_hide_product_id:
                    if trigger in [prod_id, product.alias_id]:
                        SystemStore.hidePageID(params.page_id)
                        return True

                return False

            self.addObserver(Notificator.onPaySuccess, _cbPaySuccess)

        if params.trigger_hide_identity is not None:
            def _cbHide(*args, **kwargs):
                SystemStore.hidePageID(params.page_id)
                return True

            hide_identity = Notificator.getIdentity(params.trigger_hide_identity)
            self.addObserver(hide_identity, _cbHide)

        if params.trigger_show_identity is not None:
            def _cbShow(*args, **kwargs):
                SystemStore.showPageID(params.page_id)
                return True

            show_identity = Notificator.getIdentity(params.trigger_show_identity)
            self.addObserver(show_identity, _cbShow)

    def _onTabSwitched(self, from_page_id, to_page_id):
        tab_params = StoreManager.getTabParamsById(to_page_id)
        StorePage = DemonManager.getDemon(tab_params.group_name)
        if StorePage.hasNotify() is False:
            self.removePageNotify(to_page_id)
        return False

    def _onTabClicked(self, tab):
        self.setCurrentPageID(tab.page_id)
        return False

    def _onClickedBack(self):
        prev_scene = SceneManager.getPrevSceneName() or "Menu"
        if prev_scene == "CutScene":
            prev_scene = "Menu"
        TaskManager.runAlias("AliasTransition", None, SceneName=prev_scene, IgnoreGameScene=True)
        return False

    def _onStoreSetPage(self, page_id):
        self.setCurrentPageID(page_id)
        return False

    # prefetch

    def _cbTransitionBegin(self, scene_from=None, scene_to=None, zoom_name=None):
        if scene_from == "Store":
            self.__unfetchPages()
        elif scene_to == "Store":
            self.__prefetchPages()
        return False

    def __prefetchPages(self):
        for tab in StoreManager.getTabsSettings().values():
            self.__prefetchPage(tab.page_id)

    def __prefetchPage(self, page_id):
        group_name = StoreManager.getTabParamsById(page_id).group_name
        if group_name in self.__prefetchedPages:
            return

        self.__prefetchedPages.append(group_name)

        def _cb(Success, GroupName):
            pass
        Mengine.prefetchResources(group_name, _cb, group_name)

    def __unfetchPages(self):
        for group_name in self.__prefetchedPages:
            Mengine.unfetchResources(group_name)
        self.__prefetchedPages = []

    # saves

    def _onSave(self):
        save_dict = {}
        return save_dict

    def _onLoad(self, save_dict):
        pass

    def _cbStageInit(self, stage):
        self._setupAlreadyBoughtPagesID()
        return False
