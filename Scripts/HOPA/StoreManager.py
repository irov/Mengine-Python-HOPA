from Foundation.DatabaseManager import DatabaseManager
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.Manager import Manager
from Foundation.Utils import getCurrentPlatformParams, getCurrentPublisher


class StoreManager(Manager):
    __PARAMS_TABLE_NAMES = {
        "tabs": "StoreTabs",
        "buttons": "StoreButtons",
        "redirect": "StoreRedirect"
    }

    s_tabs = {}
    s_buttons = {}

    class __Param(object):
        if _DEVELOPMENT is True:
            def __repr__(self):
                return "<{}: {}>".format(self.__class__.__name__, self.__dict__)

    class TabParam(__Param):
        def __init__(self, record):
            self.index = None
            self.page_id = StoreManager.getRecordValue(record, "PageID", cast=str)
            self.group_name = StoreManager.getRecordValue(record, "GroupName")
            self.text_id = StoreManager.getRecordValue(record, "TitleTextID", default="ID_EMPTY")
            self.selected = StoreManager.getRecordValue(record, "DefaultSelected", cast=bool, default=False)
            self.hidden = StoreManager.getRecordValue(record, "DefaultHidden", cast=bool, default=False)
            self.first_visited = StoreManager.getRecordValue(record, "DefaultVisited", cast=bool, default=True)
            self.trigger_hide_product_id = StoreManager.getRecordValue(record, "HideProductID")
            self.trigger_hide_identity = StoreManager.getRecordValue(record, "HideIdentity")
            self.trigger_show_identity = StoreManager.getRecordValue(record, "ShowIdentity")

            selected_color = StoreManager.getRecordValue(record, "SelectedTextColor")
            self.selected_color = self.convertColor(selected_color)
            idle_color = StoreManager.getRecordValue(record, "IdleTextColor")
            self.idle_color = self.convertColor(idle_color)

        def convertColor(self, text_color):
            if text_color is None:
                return None

            colors = tuple(float(color) for color in text_color.split(" ") if 0 <= float(color) <= 1)

            if len(colors) != 4:
                Trace.log("Manager", 0, "TabParam.convertColor {!r} - should be 4 values from 0 to 1".format(text_color))
                return None

            return colors

    class ButtonParam(__Param):
        def __init__(self, record):
            self.index = StoreManager.getRecordValue(record, "Index", cast=int)
            self.page_id = StoreManager.getRecordValue(record, "PageID", cast=str)
            self.button_id = StoreManager.getRecordValue(record, "ButtonID", cast=str)
            self.slot_name = StoreManager.getRecordValue(record, "SlotName")
            self.action = StoreManager.getRecordValue(record, "Action", default="purchase")
            self.product_id = StoreManager.getRecordValue(record, "ProductID", cast=str)

            # prototypes
            self.prototype_group = StoreManager.getRecordValue(record, "PrototypeGroup")
            self.button_prototype = StoreManager.getRecordValue(record, "ButtonPrototype")
            self.icon_prototype = StoreManager.getRecordValue(record, "IconPrototype")
            self.discount_submovie = StoreManager.getRecordValue(record, "DiscountSubmovie", default="discount")

            # texts
            self.price_text_id = StoreManager.getRecordValue(record, "PriceTextID", default="ID_EMPTY")
            self.restore_text_id = StoreManager.getRecordValue(record, "RestoreTextID", default=self.price_text_id)
            self.title_text_id = StoreManager.getRecordValue(record, "TitleTextID", default="ID_EMPTY")
            self.descr_text_id = StoreManager.getRecordValue(record, "DescrTextID", default="ID_EMPTY")
            self.gold_reward_text_id = StoreManager.getRecordValue(record, "GoldRewardTextID", default="ID_EMPTY")
            self.energy_reward_text_id = StoreManager.getRecordValue(record, "EnergyRewardTextID", default="ID_EMPTY")
            self.discount_text_id = StoreManager.getRecordValue(record, "DiscountTextID", default="ID_EMPTY")
            self.timer_text_id = StoreManager.getRecordValue(record, "TimerTextID", default="__ID_TEXT_CONSOLE")
            self.counter_text_id = StoreManager.getRecordValue(record, "CounterTextID", default="ID_EMPTY")

        def getPrototypesNames(self):
            prototypes = [("ButtonPrototype", self.button_prototype), ("IconPrototype", self.icon_prototype)]
            return prototypes

        def getTextIds(self):
            text_ids_keys = filter(lambda x: x.endswith("_text_id"), self.__dict__)
            text_ids = [self.__dict__[key] for key in text_ids_keys]
            return text_ids

    @staticmethod
    def checkTabParams():
        def trace(msg):
            Trace.log("System", 0, "SystemStore found error on checkTabParams: {}".format(msg))

        selected_tabs = []  # page ids with selected=True

        for tab in StoreManager.s_tabs.values():
            # Check page Selected param
            if tab.selected is True:
                selected_tabs.append(tab.page_id)
                if len(selected_tabs) > 1:
                    tab.selected = False

            # Check Page exist
            if GroupManager.hasGroup(tab.group_name) is False:
                trace("Tab with id {!r} has non-exist group {!r}".format(tab.page_id, tab.group_name))
                StoreManager.s_tabs.pop(tab.page_id)

        if len(StoreManager.s_tabs) == 0:
            return

        if len(selected_tabs) != 1:
            trace("You must set Selected=True to only one of your tab. You has 1 != {} [] selected tab!".format(len(selected_tabs), selected_tabs))

    @staticmethod
    def loadButtons(records):
        from Foundation.MonetizationManager import MonetizationManager

        def trace(params, msg):
            Trace.log("System", 0, "SystemStore got error while load buttons: [{}:{}] {}".format(params.page_id, params.button_id, msg))

        _current_locale = Mengine.getLocale()

        for record in records:
            params = StoreManager.ButtonParam(record)

            group_name = params.prototype_group
            manager = DemonManager if group_name.startswith("Demon_") else GroupManager

            prototypes_ok = True
            for param_name, prototype_name in params.getPrototypesNames():
                if prototype_name is None:
                    continue
                if manager.hasPrototype(group_name, prototype_name) is False:
                    trace(params, "Group {} has no prototype {!r} [{}]".format(group_name, prototype_name, param_name))
                    prototypes_ok = False
            if prototypes_ok is False:
                continue

            texts_ok = True
            for text_id in params.getTextIds():
                if Mengine.existText(text_id) is False:
                    trace(params, "TextID {!r} not found for locale '{}'".format(text_id, _current_locale))
                    texts_ok = False
            if texts_ok is False:
                continue

            if params.action == "purchase" and MonetizationManager.getProductInfo(params.product_id) is None:
                trace(params, "product id {} not found".format(params.product_id))
                continue

            if params.page_id not in StoreManager.s_buttons:
                StoreManager.s_buttons[params.page_id] = {}

            StoreManager.s_buttons[params.page_id][params.button_id] = params

    @staticmethod
    def loadTabs(records):
        def trace(msg):
            Trace.log("System", 0, "SystemStore got error while load tabs: {}".format(msg))

        for i, record in enumerate(records):
            params = StoreManager.TabParam(record)
            params.index = i
            if params.page_id in StoreManager.s_tabs:
                trace("Use only unique ids - {!r} already used".format(params.page_id))
            StoreManager.s_tabs[params.page_id] = params

    @staticmethod
    def loadRedirector(records):
        TYPES_BLACKLIST = ["redirect"]
        HUMAN_TABLE_NAMES = {value: key for key, value in StoreManager.__PARAMS_TABLE_NAMES.items() if key not in TYPES_BLACKLIST}

        current_publisher = getCurrentPublisher()
        if current_publisher is None:
            return

        for record in records:
            Publisher = record.get("Publisher")
            if Publisher != str(current_publisher):
                continue

            Type = HUMAN_TABLE_NAMES.get(record.get("Type"))
            if Type is None:
                redirect_table_name = StoreManager.__PARAMS_TABLE_NAMES["redirect"]
                Trace.log("Manager", 0, "{} has error in Type {!r} - choose one of them: {!r}".format(
                    redirect_table_name, record.get("Type"), HUMAN_TABLE_NAMES))
                continue

            platforms = getCurrentPlatformParams()

            for platform, b_active in platforms.items():
                if b_active is False:
                    continue

                table_name = record.get(platform)
                if table_name is None:
                    # only one platform could be True, so we don't need to continue our loop
                    break

                table_name = table_name.format(tag=StoreManager.__PARAMS_TABLE_NAMES[Type],
                                               platform=platform,
                                               publisher=Publisher)
                StoreManager.__PARAMS_TABLE_NAMES[Type] = table_name

    @staticmethod
    def reportStatus():
        SIZE = 50
        HALF_SIZE = SIZE // 2

        Trace.msg("-" * SIZE)
        Trace.msg("STORE PARAMS".center(SIZE, " "))
        Trace.msg("-" * SIZE)

        for key, table_name in StoreManager.__PARAMS_TABLE_NAMES.items():
            Trace.msg("{}:  ".format(key).rjust(HALF_SIZE) + table_name.ljust(HALF_SIZE))

        Trace.msg("-" * SIZE)

    @staticmethod
    def loadParams(module, name):
        records = DatabaseManager.getDatabaseRecords(module, name)

        if name == StoreManager.__PARAMS_TABLE_NAMES["tabs"]:
            StoreManager.loadTabs(records)
            StoreManager.checkTabParams()

        elif name == StoreManager.__PARAMS_TABLE_NAMES["buttons"]:
            StoreManager.loadButtons(records)

        elif name == StoreManager.__PARAMS_TABLE_NAMES["redirect"]:
            # should be first !!
            StoreManager.loadRedirector(records)
            StoreManager.reportStatus()

        return True

    # === Getters ======================================================================================================

    @staticmethod
    def getTabsSettings():
        """ return: dict {page_id: TabParam}"""
        return StoreManager.s_tabs

    @staticmethod
    def getButtonsSettings():
        """ return: dict {page_id: {button_id: ButtonParam}, ...}"""
        return StoreManager.s_buttons

    # specific

    @staticmethod
    def getTabParamsById(page_id, default=None):
        """ return: TabParam or None"""
        return StoreManager.s_tabs.get(page_id, default)

    @staticmethod
    def getButtonsParamsById(page_id):
        """ return: dict {button_id: ButtonParam}"""
        return StoreManager.s_buttons.get(page_id, {})

    @staticmethod
    def findPageIdByProductId(product_id):
        """ returns page id if input product inside this page """
        for page_id, page_buttons in StoreManager.getButtonsSettings().items():
            for button in page_buttons.values():
                if button.product_id == product_id:
                    return page_id
        return None
