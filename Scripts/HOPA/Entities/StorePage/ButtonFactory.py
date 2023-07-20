from HOPA.Entities.StorePage.Buttons.ButtonMixin import ButtonMixin
from HOPA.Entities.StorePage.Buttons.ButtonPurchase import ButtonPurchase
from HOPA.Entities.StorePage.Buttons.ButtonAdvert import ButtonAdvert
from HOPA.Entities.StorePage.Buttons.ButtonExchange import ButtonExchange
from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from HOPA.StoreManager import StoreManager


class ButtonFactory(object):
    allowed_actions = {
        "purchase": ButtonPurchase,
        "advert": ButtonAdvert,
        "exchange": ButtonExchange,
    }
    objects = []  # [ ConcreteButton, ... ]
    page_objects = {}  # { page_id: { button_id: ConcreteButton, ... }, ... }

    @classmethod
    def _updateButtonsParams(cls):
        if MonetizationManager.getGeneralSetting("StoreCardPriceCurrencyPosition", "left") == "left":
            price_template = "{currency}{price}"
        else:  # position is 'right'
            price_template = "{price}{currency}"
        price_template = MonetizationManager.getGeneralSetting("StoreCardPriceTemplate", price_template)
        ButtonPurchase.price_template = price_template

    @classmethod
    def createPageButtons(cls, page_id):
        cls._updateButtonsParams()

        buttons = []

        button_params = StoreManager.getButtonsParamsById(page_id)
        for param in button_params.values():
            group_name = param.prototype_group

            if group_name.startswith("Demon_"):
                group = DemonManager.getDemon(group_name)
            else:
                group = GroupManager.getGroup(group_name)

            button_movie = group.tryGenerateObjectUnique(param.button_prototype, param.button_prototype)
            icon_movie = None
            if param.icon_prototype is not None:
                icon_movie = group.tryGenerateObjectUnique(param.icon_prototype, param.icon_prototype)

            button = ButtonFactory.createButton(param, button_movie, icon_movie)
            if button is None:
                continue
            buttons.append(button)

        return buttons

    @classmethod
    def createButton(cls, params, button_movie, icon_movie):
        page_id = params.page_id

        if params.action not in cls.allowed_actions:
            Trace.log("Manager", 0, "ButtonFactory [{!r}] not found action {!r}".format(params.button_id, params.action))
            button = ButtonMixin(params, button_movie, icon_movie)
            button.cleanUp()
            return None

        ConcreteButton = cls.allowed_actions[params.action]
        button = ConcreteButton(params, button_movie, icon_movie)
        button.setPlay(True, Loop=True)

        if page_id not in cls.page_objects:
            cls.page_objects[page_id] = {}
        cls.page_objects[page_id][params.button_id] = button
        cls.objects.append(button)

        # print " * [{}] created button {} [{}] from {} for slot:{} ".format(params.page_id, params.action, params.button_id, params.prototype, params.slot_name)

        return button

    @classmethod
    def cleanPageObjects(cls, page_id):
        if len(cls.page_objects) == 0:
            return True

        if page_id not in cls.page_objects:
            Trace.log("Manager", 0, "ButtonFactory page_id {!r} not found".format(page_id))
            return False

        for button_id, button in cls.page_objects.pop(page_id).items():
            button.cleanUp()
            cls.objects.remove(button)
        return True

    @classmethod
    def cleanObjects(cls):
        # print "!!!!!!!! CLEAN OBJECTS !!!!!!!!!!"
        for button in cls.objects:
            button.cleanUp()
        cls.objects = []
        cls.page_objects = {}

    @classmethod
    def getAllButtons(cls):
        """ returns list of all created buttons """
        return cls.objects

    @classmethod
    def getPageButtons(cls, page_id):
        """ returns dict like { page_id: { button_id: ConcreteButton, ... }, ... } """
        return cls.page_objects.get(page_id, {})
