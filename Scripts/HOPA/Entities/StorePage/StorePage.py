from Foundation.DemonManager import DemonManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.Entities.StorePage.ButtonFactory import ButtonFactory
from HOPA.Entities.StorePage.Components.StorePageAdvertComponent import StorePageAdvertComponent
from HOPA.Entities.StorePage.Components.StorePageGroupComponent import StorePageGroupComponent
from HOPA.Entities.StorePage.Components.StorePageScrollComponent import StorePageScrollComponent
from HOPA.Entities.StorePage.Components.StorePageScrollVerticalComponent import StorePageScrollVerticalComponent
from HOPA.StoreManager import StoreManager
from Notification import Notification


class StorePage(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction(Type, "PageID")
        Type.addAction(Type, "Scrollable")
        Type.addAction(Type, "ScrollMode")
        Type.addAction(Type, "WaitButtons")

        Type.addAction(Type, "ColumnsCount")
        Type.addAction(Type, "OffsetX")
        Type.addAction(Type, "OffsetY")

    def __init__(self):
        super(StorePage, self).__init__()
        self.params = None
        self.content = None  # movie with all interactive content
        self.buttons = []
        self.tc = None

        self.advert_component = None
        self.scroll_component = None
        self.grouped_products_components = {}

    def _onPreparation(self):
        if self.object.hasObject("Movie2_Content") is False:
            Trace.log("Entity", 0, "StorePage [{}] not found Movie2_Content in demon inside group '{}'".format(self.PageID, self.object.parent.getName()))
            return

        self.content = self.object.getObject("Movie2_Content")
        self.params = StoreManager.getButtonsParamsById(self.PageID)
        self.buttons = ButtonFactory.createPageButtons(self.PageID)

        self.initComponents()

        self.attachButtons()

        self.updateNotify()

        if self.scroll_component is not None:
            self.scroll_component.run()

    def _onActivate(self):
        if self.advert_component is not None:
            self.advert_component.run()
        for group_component in self.grouped_products_components.values():
            group_component.run()

        self.runTaskChain()

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()
            self.tc = None

        if self.scroll_component is not None:
            self.scroll_component.stop()
            self.scroll_component = None

        if self.advert_component is not None:
            self.advert_component.stop()
            self.advert_component = None

        for group_component in self.grouped_products_components.values():
            group_component.stop()
        self.grouped_products_components = {}

        self.content = None
        self.params = None

        ButtonFactory.cleanPageObjects(self.PageID)
        self.buttons = []

    def initComponents(self):
        for button in self.buttons:
            if button.action == "advert":
                if self.advert_component is None:
                    self.advert_component = StorePageAdvertComponent(self, button)
                continue

            if button.action == "link":
                continue

            group_id = button.product_params.group_id
            if group_id is not None and group_id not in self.grouped_products_components:
                self.grouped_products_components[group_id] = StorePageGroupComponent(self, group_id)

        if self.Scrollable is True:
            if self.ScrollMode == "horizontal":
                self.scroll_component = StorePageScrollComponent(self)
            elif self.ScrollMode == "vertical":
                self.scroll_component = StorePageScrollVerticalComponent(self)
                self.scroll_component.columns_count = self.ColumnsCount
                self.scroll_component.offset_x = self.OffsetX
                self.scroll_component.offset_y = self.OffsetY

            self.scroll_component.scroll_mode = self.ScrollMode

    # ==================================================================================================================

    def runTaskChain(self):
        if len(self.buttons) == 0:
            Trace.log("Entity", 0, "Store page [{}] has no buttons to run taskchain!!!".format(self.PageID))
            return

        if self.tc is not None:
            self.tc.cancel()
        self.tc = TaskManager.createTaskChain(Name="StorePage_{}".format(self.PageID), Repeat=True)

        with self.tc as tc:
            for button, source_race in tc.addRaceTaskList(self.buttons):
                source_race.addScope(button.scopeClick)
                source_race.addScope(button.scopeAction)
                source_race.addFunction(self._cbButtonAction, button)

    def _cbButtonAction(self, button):
        if button.hasNotify() is True:
            return

        if button.id in self.WaitButtons:
            button.removeNotify()
            self.object.delParam("WaitButtons", button.id)

        if len(self.WaitButtons) == 0:
            Notification.notify(Notificator.onStorePageNewActionsEnd, self.PageID)

    def attachButtons(self):
        ordered_buttons = sorted(self.buttons, key=lambda param: param.params.index, reverse=True)
        for button in ordered_buttons:
            slot_name = button.params.slot_name
            if self.content.hasMovieSlot(slot_name) is False:
                Trace.log("Entity", 0, "StorePage [{}] not found slot {!r}".format(self.PageID, slot_name))
                continue
            slot = self.content.getMovieSlot(slot_name)
            node = button.movie.getEntityNode()
            slot.addChild(node)

            button.setEnable(True)

            if slot_name == "content" and self.scroll_component is not None:
                self.scroll_component.adjustButton(button)

    # === Working with notify indicator ================================================================================

    def updateNotify(self):
        """ used for update notify on buttons that requires a click """

        Store = DemonManager.getDemon("Store")

        for button in self.buttons:
            if button.hasNotify() is False:
                button.removeNotify()
                if button.id in self.WaitButtons:
                    self.object.delParam("WaitButtons", button.id)
            else:
                if button.id not in self.WaitButtons:
                    self.object.appendParam("WaitButtons", button.id)
                notify_movie = Store.tryGenerateObjectUnique("Movie2_RedDot", "Movie2_RedDot", Enable=True)
                button.attachNotify(notify_movie)

        if len(self.WaitButtons) != 0:
            Notification.notify(Notificator.onStorePageNewActions, self.PageID)
        elif len(self.WaitButtons) == 0:
            Notification.notify(Notificator.onStorePageNewActionsEnd, self.PageID)

    def hasNotify(self):
        if len(self.WaitButtons) != 0:
            return True
        return False
