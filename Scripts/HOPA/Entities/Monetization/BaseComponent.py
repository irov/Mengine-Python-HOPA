from Foundation.GroupManager import GroupManager
from Foundation.MonetizationManager import MonetizationManager
from Notification import Notification


class BaseComponent(object):
    _settings = {}
    _defaults = {}

    def __init__(self):
        self._observers = []

        self.enable = self._getMonetizationParam("is_enable", False) is True

        self.product = None
        if "product_id" in self._settings:
            self._product_lookup_id = str(self._getMonetizationParam("product_id"))
            if MonetizationManager.hasProductInfo(self._product_lookup_id):
                self.product = MonetizationManager.getProductInfo(self._product_lookup_id)

        self.env = self._getMonetizationParam("env", self.__class__.__name__)
        self.alias_id = self._getMonetizationParam("alias_id")
        self.text_id = self._getMonetizationParam("text_id", "ID_EMPTY")
        self.text_args = None

        self.group_name = self._getMonetizationParam("group")
        self.group = GroupManager.getGroup(self.group_name) if GroupManager.hasGroup(self.group_name) else None
        self.movie_name = self._getMonetizationParam("movie")

        self._createParams()

    def _error(self, message):
        error_log = "Monetization component {} ERROR: {}".format(self.__class__.__name__, message)
        Trace.log("Entity", 0, error_log)

    def _getMonetizationParam(self, key, default=None):
        param = MonetizationManager.getGeneralSetting(self._settings.get(key), self._defaults.get(key, default))
        return param

    def _createParams(self):
        """ creates additional params for module """
        return

    def _check(self):
        return True

    def initialize(self):
        if self.isEnable() is False:
            return False

        if self._check() is False:
            self.enable = False
            return False

        return self._initialize()

    def _initialize(self):
        return True

    def run(self):
        self._setupText()
        self._run()

    def _run(self):
        pass

    def cleanUp(self):
        for observer in self._observers:
            Notification.removeObserver(observer)
        self._observers = None
        self._cleanUp()

    def _cleanUp(self):
        pass

    def stop(self):
        self.cleanUp()
        self._stop()

    def _stop(self):
        pass

    def _setupText(self):
        if self.alias_id is None:
            return

        Mengine.setTextAlias(self.env, self.alias_id, self.text_id)

        if self.text_args and "%s" in Mengine.getTextFromId(self.text_id):
            Mengine.setTextAliasArguments(self.env, self.alias_id, *self.text_args)

    def save(self):
        return self._save()

    def _save(self):
        return {}

    def load(self, save):
        self._load(save)

    def _load(self, save):
        return

    # utils

    def addObserver(self, notificator, fn, *args, **kwargs):
        observer = Notification.addObserver(notificator, fn, *args, **kwargs)
        self._observers.append(observer)

    def isEnable(self):
        return self.enable

    def getProductId(self):
        if self.product is not None:
            return self.product.id
        return None

    def getProductCurrency(self):
        if self.product is not None:
            return self.product.currency
        return None

    def getProductPrice(self):
        if self.product is not None:
            return self.product.price
        return None
