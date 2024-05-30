from Foundation.DemonManager import DemonManager
from Foundation.Systems.SystemMonetization import SystemMonetization
from Foundation.Utils import getCurrentPublisher


class Coin(object):

    def __init__(self, parent):
        self.parent = parent
        self.store = DemonManager.getDemon(SystemMonetization.game_store_name)
        self.movie = None

        currency = self.parent.getProductCurrency()
        prototype_template = {
            "Gold": "Movie2_Coin_{publisher}",
            "default": "Movie2_{currency}_{publisher}",
        }
        prototype_name = prototype_template.get(currency, prototype_template["default"]).format(
            publisher=getCurrentPublisher(),
            currency=currency
        )
        self.prototype_name = prototype_name

    def initialize(self):
        if self.store.hasPrototype(self.prototype_name) is True:
            self.parent.addObserver(Notificator.onLayerGroupEnable, self._onActivate)
            self.parent.addObserver(Notificator.onLayerGroupRelease, self._onDeactivate)
        else:
            Trace.log("Entity", 0, "{!r} has no prototype {!r}".format(self.store.getName(), self.prototype_name))
            return False
        return True

    def _destroy(self):
        if self.movie is None:
            return

        self.movie.removeFromParent()
        self.movie.onDestroy()
        self.movie = None

        movie = self.parent.group.getObject(self.parent.movie_name)
        movie.setEnable(False)

    def _create(self):
        if self.movie is not None:
            self._destroy()

        coin = self.store.generateObjectUnique(self.prototype_name, self.prototype_name)
        coin.setTextAliasEnvironment(self.parent.env)
        self.movie = coin

        movie = self.parent.group.getObject(self.parent.movie_name)
        slot = movie.getMovieSlot("coin")
        slot.addChild(coin.getEntityNode())

        coin.setEnable(True)
        movie.setEnable(True)

    def cleanUp(self):
        self._destroy()
        self.parent = None
        self.store = None

    # observers

    def _onActivate(self, name):
        if self.parent.group_name != name:
            return False

        self._create()

        return False

    def _onDeactivate(self, name):
        if self.parent.group_name != name:
            return False

        self._destroy()

        return False
