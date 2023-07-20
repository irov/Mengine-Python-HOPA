from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.PolicyManager import PolicyManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from Foundation.Utils import SimpleLogger
from HOPA.Entities.Store.TabSection import TabSection
from HOPA.Entities.StorePage.ButtonFactory import ButtonFactory
from HOPA.StoreManager import StoreManager
from Notification import Notification


_Log = SimpleLogger("Store")


class Store(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "CurrentPageID",
                       Update=Store._cbUpdatePageID)
        Type.addAction(Type, "UnvisitedPagesID",
                       Append=Store._cbAppendUnvisitedPagesID,
                       Remove=Store._cbRemoveUnvisitedPagesID)
        Type.addAction(Type, "HiddenPagesID",
                       Append=Store._cbAppendHiddenPagesID,
                       Remove=Store._cbRemoveHiddenPagesID)

    def __init__(self):
        super(Store, self).__init__()
        self.current_tab = None
        self.tab_section = None

    def isStoreEnable(self):
        return self.object.isStoreEnable()

    def onPreparation(self):
        if SystemManager.hasSystem("SystemStore") is False:
            Trace.log("Entity", 0, "Store requires SystemStore for work!!!!!")

        PolicyAuth = PolicyManager.getPolicy("Authorize", "PolicyDummy")
        TaskManager.runAlias(PolicyAuth, None)

        self.createTabs()

        self._cbUpdatePageID(self.CurrentPageID)

    def onActivate(self):
        if self.tab_section is not None:
            self.tab_section.runTaskChain()

    def onDeactivate(self):
        if self.tab_section is not None:
            self.tab_section.cleanUp()
        self.tab_section = None

        ButtonFactory.cleanObjects()
        self.current_tab = None

    # ----

    def createTabs(self):
        if GroupManager.hasGroup("StoreTabs") is False:
            if _DEVELOPMENT is True:
                Trace.msg_err("Store doesn't find group StoreTabs")
            return False

        StoreTabs = GroupManager.getGroup("StoreTabs")

        if StoreTabs.isActive() is False:
            Trace.log("Entity", 0, "Store.createTabs failed - enable group StoreTabs in DefaultSlots!")
            return False

        if StoreTabs.hasObject("Movie2_Tabs") is False:
            Trace.log("Entity", 0,
                      "Store.createTabs failed - not found parent movie {!r} in group StoreTabs".format("Movie2_Tabs"))
            return False

        if StoreTabs.hasObject("Movie2_BG") is True:
            # used for correct bg socket block, but not necessary
            bg_movie = StoreTabs.getObject("Movie2_BG")
            bg_movie.setInteractive(True)

        tabs_movie = StoreTabs.getObject("Movie2_Tabs")
        params = StoreManager.getTabsSettings()

        tab_section = TabSection(StoreTabs, tabs_movie, params)
        tab_section.create(ignored_pages=self.HiddenPagesID, unvisited_pages=self.UnvisitedPagesID)

        self.tab_section = tab_section

        if StoreTabs.hasObject("Movie2_Content") is False:
            Trace.log("Entity", 0,
                      "Store.createTabs failed - not found movie {!r} - scroll disabled".format("Movie2_Content"))
            return False
        content_movie = StoreTabs.getObject("Movie2_Content")
        tab_section.setupVirtualArea(content_movie, slot_name="tabs", socket_name="touch")

    # page handler

    def _openFirstTab(self):
        if len(self.tab_section.tabs) == 0:
            Trace.log("Entity", 0, "Can't change page - 0 tabs in tab_section!!")
            return
        tab = self.tab_section.getFirstTab()
        self.object.setParam("CurrentPageID", tab.page_id)

    def _cbUpdatePageID(self, page_id):
        if self.tab_section is None:
            return

        if page_id is None:
            self._openFirstTab()
            return

        tab = self.tab_section.getTab(page_id)

        if tab is None:
            self._openFirstTab()
            return

        self._changePage(tab)

    def _cbAppendUnvisitedPagesID(self, index, page_id):
        _Log("[Append UnvisitedPagesID] index=%s page_id=%s" % (index, page_id))
        if self.tab_section is None:
            return

        tab = self.tab_section.getTab(page_id)
        tab.setVisited(False)

    def _cbRemoveUnvisitedPagesID(self, index, page_id, old):
        _Log("[Remove UnvisitedPagesID] index=%s page_id=%s old=%s" % (index, page_id, old))
        if self.tab_section is None:
            return

        tab = self.tab_section.getTab(page_id)
        tab.setVisited(True)

    def _cbAppendHiddenPagesID(self, index, page_id):
        _Log("[Append HiddenPagesID] index=%s page_id=%s" % (index, page_id))
        if self.tab_section is None:
            return

        self.tab_section.remove_tab(page_id)
        self.object.setParam("CurrentPageID", None)

    def _cbRemoveHiddenPagesID(self, index, page_id, old):
        _Log("[Remove HiddenPagesID] index=%s page_id=%s old=%s" % (index, page_id, old))
        if self.tab_section is None:
            return

        # todo: add new tab

    def _changePage(self, tab):
        """ For changing page you should update CurrentPageID, then in cb this method will be called
                usage:  Store.setParam("CurrentPageID", "some_page_id")
        """

        current_page_id = self.current_tab.page_id if self.current_tab else None

        if current_page_id == tab.page_id:
            # fixme: store do page changing twice
            return

        def _cb(isSkip):
            self.tab_section._cbTabClicked(tab)  # <- set selected button
            Notification.notify(Notificator.onStoreTabSwitched, current_page_id, tab.page_id)
            self.current_tab = tab

        tc_name = "StoreTabSwitching_{}_{}".format(current_page_id, tab.page_id)
        with TaskManager.createTaskChain(Name=tc_name, Cb=_cb) as tc:
            if self.current_tab is not None:
                cur_page_group_name = self.current_tab.params.group_name
                tc.addTask("TaskSceneLayerGroupEnable", LayerName=cur_page_group_name, Value=False)

            next_page_group_name = tab.params.group_name
            tc.addTask("TaskSceneLayerGroupEnable", LayerName=next_page_group_name, Value=True)
        return False
