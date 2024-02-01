from Foundation.MonetizationManager import MonetizationManager
from Foundation.SystemManager import SystemManager


class StoreCardMixin(object):
    ALIAS_PRICE = "$AliasGameStoreCardPrice"
    ALIAS_DESCR = "$AliasGameStoreCardDescr"
    PRICE_TEMPLATE = "{}"

    def __init__(self):
        self.card_id = None
        self.prod_id = None

        self.movie_card = None
        self.movie_image = None

        self.prod_params = None
        self.params = None
        self.image_params = None

        self.env = None

    def init(self, card_id, card_movie, image_movie, params):
        self.card_id = card_id
        self.prod_id = params.prod_id

        self.movie_card = card_movie
        self.movie_image = image_movie

        self.prod_params = MonetizationManager.getProductInfo(self.prod_id)
        self.params = params
        self.image_params = MonetizationManager.getImageParamsById(card_id)
        self.env = "card_%s" % self.card_id

        self.enableImageLayer()

        card_movie.addChildToSlot(image_movie.getEntityNode(), "image")

        self.setTexts()

    def cleanUp(self):
        image_node = self.movie_image.getEntityNode()
        self.movie_card.removeFromParentSlot(image_node, "image")

        self.movie_image.onDestroy()
        self.movie_image = None

        self.movie_card.removeFromParent()
        self.movie_card.onDestroy()
        self.movie_card = None

        self.card_id = None
        self.params = None

    def setEnable(self, state):
        self.movie_card.setEnable(state)

    def setBlock(self, state):
        self.movie_card.setBlock(state)

    def enableImageLayer(self):
        layer_name = self.image_params.layer_name
        if layer_name is None:
            return

        resource_movie = self.movie_image.getResourceMovie()
        composition_name = self.movie_image.getCompositionName()

        layers = resource_movie.getCompositionLayers(composition_name)
        for layer in layers:
            _type = layer["type"]
            _name = layer["name"]

            if _type != "Image":
                continue

            state = _name == layer_name
            disable_layers = self.movie_image.getParam("DisableLayers")
            if state is False and _name not in disable_layers:
                self.movie_image.appendParam("DisableLayers", _name)
            elif state is True and _name in disable_layers:
                self.movie_image.delParam("DisableLayers", _name)

    def setTexts(self):
        self.movie_card.setTextAliasEnvironment(self.env)
        Mengine.setTextAlias(self.env, self.ALIAS_PRICE, MonetizationManager.getGeneralSetting("StoreCardPriceTextID"))
        Mengine.setTextAlias(self.env, self.ALIAS_DESCR, MonetizationManager.getGeneralSetting("StoreCardDescrTextID"))

        self._setPrice()
        self._setDescr()

    def _setPrice(self):
        price = MonetizationManager.getProductPrice(self.prod_id)
        currency = MonetizationManager.getCurrentCurrencySymbol() or ""

        Mengine.setTextAliasArguments(self.env, self.ALIAS_PRICE,
                                      self.PRICE_TEMPLATE.format(price=str(price), currency=currency))

    def _setDescr(self):
        descr_text_id = self.params.descr
        descr_text = Mengine.getTextFromId(descr_text_id)
        if "%s" in descr_text:
            descr_text = descr_text % self._getRewardArg()
        Mengine.setTextAliasArguments(self.env, self.ALIAS_DESCR, descr_text)

    def _getRewardArg(self):
        return ""

    # scopes

    def scopeInteract(self, source):
        if SystemManager.hasSystem("SystemMonetization") is True:
            source.addScope(self._scopeInteract)
        else:
            source.addScope(self._scopeInteractDummy)

    def _scopeInteract(self, source):
        source.addDummy()

    def _scopeInteractDummy(self, source):
        source.addDummy()
