from Foundation.MonetizationManager import MonetizationManager


class ButtonMixin(object):
    aliases = {}
    _submovies = []
    action = None

    if _DEVELOPMENT is True:
        def __repr__(self):
            return "<{} [{}:{}]>".format(self.__class__.__name__, self.params.page_id, self.id)

    def __init__(self, params, button_movie, icon_movie):
        self.id = params.button_id
        self.params = params
        self.product_params = MonetizationManager.getProductInfo(params.product_id)

        self.movie = button_movie
        self.icon_movie = icon_movie
        if icon_movie is not None:
            self.attach("icon", icon_movie)
        self.notify_movie = None

        self.env = str(self.id)
        self._initText()

        self._prepare()

    # Working with text

    def _getTextID(self, alias_id):
        alias_and_text_ids = self._getAliasAndTextID()
        alias = self.aliases[alias_id]
        text_id = alias_and_text_ids[alias]
        return text_id

    def _getAliasAndTextID(self):
        return {}

    def _initText(self):
        self.movie.setTextAliasEnvironment(self.env)

        alias_and_text_ids = self._getAliasAndTextID()
        for alias, text_id in alias_and_text_ids.items():
            Mengine.setTextAlias(self.env, alias, text_id)

        self.setText()

    def setText(self):
        """ method that setups text arguments to the aliases """

    def setTextArguments(self, alias_id, *args):
        """ alias_id is from param aliases"""
        if alias_id not in self.aliases:
            Trace.log("Entity", 0, "Not found alias_id={!r} in aliases dict. Available: {}".format(alias_id, self.aliases.keys()))
            return
        alias = self.aliases[alias_id]
        Mengine.setTextAliasArguments(self.env, alias, *args)

    # Working with attachments and states

    def _prepare(self):
        pass

    def hasNotify(self):
        return False

    def attach(self, slot_name, movie):
        node = movie.getEntityNode()
        self.movie.addChildToSlot(node, slot_name)

    def detach(self, slot_name, movie):
        node = movie.getEntityNode()
        self.movie.removeFromParentSlot(node, slot_name)

    def attachNotify(self, movie):
        if self.notify_movie is not None:
            self.removeNotify()

        self.attach("notify", movie)
        self.notify_movie = movie

    def removeNotify(self):
        if self.notify_movie is None:
            return

        self.detach("notify", self.notify_movie)
        self.notify_movie.onDestroy()
        self.notify_movie = None

    def setEnable(self, state):
        self.movie.setEnable(state)
        if self.icon_movie is not None:
            self.icon_movie.setEnable(state)

    def setBlock(self, state):
        self.movie.setBlock(state)

    def hasSubmovie(self, submovie_name):
        for movie in self.movie.eachMovies():
            if movie.entity.hasSubMovie(submovie_name) is True:
                return True
        return False

    def setEnableSubmovie(self, submovie_name, state):
        if self.hasSubmovie(submovie_name) is False:
            Trace.log("Entity", 1, "Store Button {} has no submovie {}".format(self.id, submovie_name))
            return

        for movie in self.movie.eachMovies():
            disable_layers = movie.getParam("DisableSubMovies")
            if state is True and submovie_name in disable_layers:
                movie.delParam("DisableSubMovies", submovie_name)
            elif state is False and submovie_name not in disable_layers:
                movie.appendParam("DisableSubMovies", submovie_name)

    def setPlay(self, state, Loop=True):
        for movie in self.movie.eachMovies():
            movie.setLoop(Loop)
            movie.setPlay(state)

            # todo: play, loop for each submovie (from _submovies)
            #       animatable.play, loop is not working because of "not initialized error"

    # CleanUp

    def cleanUp(self):
        if self.icon_movie is not None:
            self.icon_movie.removeFromParent()
            self.icon_movie.onDestroy()
            self.icon_movie = None

        self.removeNotify()

        if self.movie is not None:
            self.movie.removeFromParent()
            self.movie.onDestroy()
            self.movie = None

        self.params = None

    # Scopes

    def scopeClick(self, source):
        source.addScope(self._scopeClick)
        source.addNotify(Notificator.onStorePageButtonClick, self)

    def _scopeClick(self, source):
        source.addTask("TaskMovie2ButtonClick", isDown=False, Movie2Button=self.movie)

    def scopeAction(self, source):
        source.addScope(self._scopeAction)

    def _scopeAction(self, source):
        source.addBlock()
