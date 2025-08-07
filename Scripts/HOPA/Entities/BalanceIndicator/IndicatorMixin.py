from Foundation.MonetizationManager import MonetizationManager

class IndicatorMixin(object):
    type = None
    icon_tag = None
    text_alias = None
    alias_env = ""
    text_id = None
    identity = None
    prepare_load_text = "..."

    if _DEVELOPMENT is True:
        def __repr__(self):
            return "<Indicator of {}: {}>".format(self.type, self.__dict__)

    def __init__(self):
        self.bg_movie = None
        self.icon_movie = None
        self.observers = []

    def setShow(self, state):
        if self.bg_movie is not None:
            self.bg_movie.setEnable(state)

    def isShow(self):
        if self.bg_movie is not None:
            return self.bg_movie.getEnable() is True
        else:
            return False

    def _getBackgroundName(self):
        return "Movie2Button_{}Indicator".format(self.type)

    def _getIconName(self):
        return "Movie2_{}_{}".format(self.icon_tag, Utils.getCurrentPublisher())

    def isEnabled(self):
        if MonetizationManager.isMonetizationEnable() is False:
            return False
            pass

        """ is allowed to be enabled in this game version """
        key = "BalanceIndicator{}Enable".format(self.type)
        return MonetizationManager.getGeneralSetting(key, True) is True

    def _prepareDisable(self, parent):
        bg_name = self._getBackgroundName()
        if parent.hasObject(bg_name) is True:
            bg_movie = parent.getObject(bg_name)
            bg_movie.setEnable(False)
        return True

    def prepare(self, parent, icon_provider_object):
        if self.isEnabled() is False:
            return self._prepareDisable(parent)

        Mengine.setTextAlias(self.alias_env, self.text_alias, self.text_id)
        self.refreshIndicatorText(self.prepare_load_text)

        bg_name = self._getBackgroundName()
        if parent.hasObject(bg_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found object {!r} in {}"
                      .format(self.type, bg_name, parent.getName()))
            return False

        icon_name = self._getIconName()
        if icon_provider_object.hasPrototype(icon_name) is False:
            Trace.log("Entity", 0, "Indicator {!r} - not found prototype {!r} in {}"
                      .format(self.type, icon_name, icon_provider_object.getName()))
            return False

        bg_movie = parent.getObject(bg_name)
        object_name = "Movie2_{}".format(self.type)
        try:
            icon_movie = icon_provider_object.generateIcon(object_name, icon_name, Enable=True)
        except AttributeError:
            icon_movie = icon_provider_object.generateObjectUnique(object_name, icon_name, Enable=True)

        icon_node = icon_movie.getEntityNode()
        icon_node.removeFromParent()
        # we can't do properly slot check, so just addChild and pray that it would be ok
        bg_movie.addChildToSlot(icon_node, "icon")
        # setShow will be called later

        self.bg_movie = bg_movie
        self.icon_movie = icon_movie

        self.observers = [
            Notification.addObserver(self.identity, self.refreshIndicatorText)
        ]

        return True

    def cleanUp(self):
        for observer in self.observers:
            Notification.removeObserver(observer)
        self.observers = []

        bg_movie = self.bg_movie
        icon_movie = self.icon_movie

        if bg_movie is not None:
            bg_movie.removeFromParentSlot(icon_movie.getEntityNode(), "icon")
            icon_movie.onDestroy()

        self.bg_movie = None
        self.icon_movie = None

    def _cbBalanceChanged(self, balance):
        return self.refreshIndicatorText(balance)

    def refreshIndicatorText(self, balance):
        """ updates balance text, must return True if you want to stop refreshing """
        Mengine.setTextAliasArguments(self.alias_env, self.text_alias, str(balance))
        return False

    def scopeClick(self, source):
        if self.bg_movie is not None:
            source.addTask("TaskMovie2ButtonClick", Movie2Button=self.bg_movie)
        else:
            source.addBlock()

    def scopeClicked(self, source):
        source.addNotify(Notificator.onIndicatorClicked, self.type)
