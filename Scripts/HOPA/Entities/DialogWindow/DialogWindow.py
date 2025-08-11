from Event import Event
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.Task.Semaphore import Semaphore
from Foundation.TaskManager import TaskManager
from Foundation.Utils import SimpleLogger
from HOPA.DialogWindowManager import DialogWindowManager

Log = SimpleLogger("DialogWindow", enable=False)

class DialogWindow(BaseEntity):
    EVENT_WINDOW_DISAPPEAR = Event("onDialogWindowDisappear")
    EVENT_WINDOW_APPEAR = Event("onDialogWindowAppear")

    # Aliases
    ID_ALIAS_ENV = ""
    ID_ALIAS_TITLE = "$DialogWindow_Title"
    ID_ALIAS_QUESTION = "$DialogWindow_Question"
    ID_ALIAS_CONFIRM = "$DialogWindow_Confirm"
    ID_ALIAS_CANCEL = "$DialogWindow_Cancel"
    ID_ALIAS_URL_LEFT = "$DialogWindow_UrlLeft"
    ID_ALIAS_URL_RIGHT = "$DialogWindow_UrlRight"
    ID_ALIAS_URL_CENTER = "$DialogWindow_UrlCenter"
    ID_ALIAS_ICON_VALUE = "$DialogWindow_IconValue"

    ALIAS_TO_TEXT = {
        "title": ID_ALIAS_TITLE,
        "question": ID_ALIAS_QUESTION,
        "confirm": ID_ALIAS_CONFIRM,
        "cancel": ID_ALIAS_CANCEL,
        "url_left": ID_ALIAS_URL_LEFT,
        "url_right": ID_ALIAS_URL_RIGHT,
        "url_center": ID_ALIAS_URL_CENTER,
        "icon_value": ID_ALIAS_ICON_VALUE
    }

    # Movies
    MOV_EFFECT_APPEAR = "Movie2_Appear"
    MOV_EFFECT_DISAPPEAR = "Movie2_Disappear"
    MOV_DIALOG_PLATE = "Movie2_Dialog_Plate"
    BTN_CONFIRM = "Movie2Button_Confirm"
    BTN_CANCEL = "Movie2Button_Cancel"

    # Content Styles movies
    CONTENT_STYLES = ["default", "urls", "icon"]
    MOV_URLS = "Movie2_ContentUrls"
    MOV_ICON = "Movie2_ContentIcon"
    MOV_DEFAULT = "Movie2_ContentDefault"

    # Texts
    ID_TEXT_EMPTY = "ID_EMPTY"

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

    def __init__(self):
        super(DialogWindow, self).__init__()
        self.content = {}
        self.effects = {}
        self.texts = {}  # keys like in DialogWindow.ALIAS_TO_TEXT
        self.args = {}  # /\
        self.urls = {}  # 'url_left', 'url_right', 'url_center'
        self.__tcs = []
        self.__wait = Semaphore(False, "DialogWindowWaitWindow")
        self.current_effect = None
        self.__onCreateNewProfileObserver = None
        self.current_content_movie = None
        self.content_style = {}

    def _onPreparation(self):
        self.__initMovies()
        self.__initTexts()

        self.__onCreateNewProfileObserver = Notification.addObserver(Notificator.onCreateNewProfile, self.__restoreEffects)

    def _onDeactivate(self):
        for tc in self.__tcs:
            tc.cancel()
        self.__tcs = []

        self._setEnableWindow(False)
        Notification.removeObserver(self.__onCreateNewProfileObserver)

    # Scopes ///////////////////////////////////////////////////////////////////////////////////////////////////////////

    def scopeOpenWindow(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        source.addFunction(Log, "appear starts...")

        source.addFunction(self._setEnableWindow, True)
        if None in [appear_effect, disappear_effect]:
            Trace.msg("<DialogWindow> can't find effects for scope OpenWindow...")
        else:
            source.addEnable(appear_effect)
            source.addPlay(appear_effect, Wait=True)
            source.addDisable(appear_effect)
            source.addEnable(disappear_effect)
            source.addFunction(self.__attachWindowToEffect, "disappear")

        source.addFunction(DialogWindow.EVENT_WINDOW_APPEAR)
        source.addFunction(Log, "...appear done")

    def scopeCloseWindow(self, source):
        appear_effect = self.effects.get("appear", None)
        disappear_effect = self.effects.get("disappear", None)

        source.addFunction(Log, "disappear starts...")

        if None in [appear_effect, disappear_effect]:
            Trace.msg("<DialogWindow> can't find effects for scope CloseWindow...")
        else:
            source.addEnable(disappear_effect)
            source.addPlay(disappear_effect, Wait=True)
            source.addDisable(disappear_effect)
            source.addEnable(appear_effect)
            source.addFunction(self.__attachWindowToEffect, "appear")
        source.addFunction(self._setEnableWindow, False)

        source.addFunction(DialogWindow.EVENT_WINDOW_DISAPPEAR)
        source.addFunction(Log, "...disappear done")

    def scopeRaceClickButtons(self, source):
        with source.addRaceTask(2) as (confirm, cancel):
            confirm.addTask("TaskMovie2ButtonClick", Movie2Button=self.content["confirm"])
            confirm.addNotify(Notificator.onDialogWindowConfirm)

            cancel.addTask("TaskMovie2ButtonClick", Movie2Button=self.content["cancel"])
            cancel.addNotify(Notificator.onDialogWindowCancel)

    def scopeClickUrls(self, source):
        movie_urls = self.content_style.get("urls")
        if movie_urls is None or len(self.urls) == 0:
            source.addBlock()

        for (socket_name, url), race_click in source.addRaceTaskList(self.urls.items()):
            race_click.addTask("TaskMovie2SocketClick", Movie2=movie_urls, SocketName=socket_name, AutoEnable=True)
            race_click.addFunction(Mengine.openUrlInDefaultBrowser, url)

    # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def __initMovies(self):
        if self.object.hasObject(DialogWindow.MOV_DIALOG_PLATE):
            self.content["plate"] = self.object.getObject(DialogWindow.MOV_DIALOG_PLATE)
            self.content["plate"].setInteractive(True)
        if self.object.hasObject(DialogWindow.BTN_CONFIRM):
            self.content["confirm"] = self.object.getObject(DialogWindow.BTN_CONFIRM)
        if self.object.hasObject(DialogWindow.BTN_CANCEL):
            self.content["cancel"] = self.object.getObject(DialogWindow.BTN_CANCEL)
        if self.object.hasObject(DialogWindow.MOV_URLS):
            self.content_style["urls"] = self.object.getObject(DialogWindow.MOV_URLS)
            self.content_style["urls"].setEnable(False)
        if self.object.hasObject(DialogWindow.MOV_ICON):
            self.content_style["icon"] = self.object.getObject(DialogWindow.MOV_ICON)
            self.content_style["icon"].setEnable(False)
        if self.object.hasObject(DialogWindow.MOV_DEFAULT):
            self.content_style["default"] = self.object.getObject(DialogWindow.MOV_DEFAULT)
            self.content_style["default"].setEnable(False)

        if self.object.hasObject(DialogWindow.MOV_EFFECT_APPEAR):
            self.effects["appear"] = self.object.getObject(DialogWindow.MOV_EFFECT_APPEAR)
        if self.object.hasObject(DialogWindow.MOV_EFFECT_DISAPPEAR):
            self.effects["disappear"] = self.object.getObject(DialogWindow.MOV_EFFECT_DISAPPEAR)

        Log("loaded effects: {}, loaded content: {}".format(self.effects.keys(), self.content.keys()))

        if self.content["plate"].hasSlot("buttons") is True:
            buttons_slot = self.content["plate"].getMovieSlot("buttons")
            confirm_node = self.content["confirm"].getEntityNode()
            cancel_node = self.content["cancel"].getEntityNode()
            buttons_slot.addChild(confirm_node)
            buttons_slot.addChild(cancel_node)
        else:
            Trace.log("Entity", 0, "DialogWindow.__initMovies: movie 'Dialog_Plate' should has slot 'buttons'")

        self.__attachWindowToEffect("appear")  # default effect
        for movie in self.content.values():
            movie.setEnable(True)
        for movie in self.effects.values():
            movie.setEnable(False)

    def __attachContentMovie(self, movie_type):
        movie_content = self.content_style.get(movie_type)
        movie_content.setEnable(True)
        movie_content_node = movie_content.getEntityNode()

        if self.content["plate"].hasSlot("content") is True:
            content_slot = self.content["plate"].getMovieSlot("content")
            content_slot.addChild(movie_content_node)
            self.current_content_movie = movie_content

    def __attachContentIcon(self, icon_obj):
        if icon_obj is None:
            return

        if self.current_content_movie == self.content_style["icon"]:
            icon_slot = self.content_style["icon"].getMovieSlot("icon")
            icon_obj_node = icon_obj.getEntityNode()
            icon_slot.addChild(icon_obj_node)

    def __deattachIcon(self, icon_obj):
        if icon_obj is not None:
            icon_obj.returnToParent()

    def __deattachContentMovie(self):
        self.current_content_movie.returnToParent()
        self.current_content_movie.setEnable(False)

    def __initTexts(self):
        for alias in DialogWindow.ALIAS_TO_TEXT.values():
            Mengine.setTextAlias(DialogWindow.ID_ALIAS_ENV, alias, DialogWindow.ID_TEXT_EMPTY)

    def __changeTexts(self, text_ids=None, text_args=None):
        if text_ids is None:
            text_ids = self.texts
        elif isinstance(text_ids, (dict, DialogWindowManager.PresetParams)) is False:
            raise TypeError("text_ids must be dict, where usable keys is: {}".format(DialogWindow.ALIAS_TO_TEXT.keys()))

        if text_args is None:
            text_args = self.args
        elif isinstance(text_args, dict) is False:
            raise TypeError("text_args must be dict, usable keys is: {}".format(DialogWindow.ALIAS_TO_TEXT.keys()))

        for key, alias in DialogWindow.ALIAS_TO_TEXT.items():
            text_id = text_ids.get(key, DialogWindow.ID_TEXT_EMPTY)
            Mengine.removeTextAliasArguments(DialogWindow.ID_ALIAS_ENV, alias)
            Mengine.setTextAlias(DialogWindow.ID_ALIAS_ENV, alias, text_id)

            if text_args is not None:
                args = text_args.get(key, None)
                if args is not None:
                    Mengine.setTextAliasArguments(DialogWindow.ID_ALIAS_ENV, alias, *args)

        self.texts = text_ids

    def __setupUrls(self, urls=None):
        if urls is None:
            return
        keys = ['url_left', 'url_center', 'url_right']
        if isinstance(urls, dict) is False:
            raise TypeError("urls must be dict, where keys is: {}".format(keys))

        for key in keys:
            url = urls.get(key)
            if url is not None:
                if isinstance(url, unicode) is False:
                    url = unicode(url, "utf-8")
                self.urls[key] = url

        Log("loaded {} urls: {}".format(len(self.urls), self.urls.items()))

    def __attachWindowToEffect(self, effect):
        window_movie = self.content["plate"]
        effect_movie = self.effects.get(effect, None)
        if effect_movie is None:
            Trace.log("Entity", 0, "DialogWindow.__attachWindowToEffect: can't find effect '{}' in self.effects {}".format(effect, self.effects.keys()))
            return

        slot = effect_movie.getMovieSlot("window")
        if slot is not None:
            window_node = window_movie.getEntityNode()
            window_node.removeFromParent()
            slot.addChild(window_node)
        else:
            Trace.log("Entity", 0, "DialogWindow.__attachWindowToEffect: movie '{}' should has slot 'window'".format(effect_movie.getName()))

        effect_movie.setLastFrame(False)  # set first frame
        self.current_effect = effect
        Log("plate attached to '{}' effect".format(effect))

    def _setEnableWindow(self, state):
        for movie in self.content.values():
            movie.setEnable(state)

    def __restoreEffects(self, *args, **kwargs):
        for movie in self.effects.values():
            movie.setEnable(False)
        return True

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def run(self, content_style=None, text_ids=None, urls=None, text_args=None, icon_obj=None):
        """ content_style: style of content from DialogWindow.CONTENT_STYLES (default is 'default')
            text_ids: dict with keys like in DialogWindow.ALIAS_TO_TEXT
            urls: dict with urls: 'url_left', 'url_center', 'url_right'
            text_args_dict: dict with arguments for text_ids, keys should be iterable
            icon_obj: ObjectMovie2 that would be attached to content
        """

        if content_style is None:
            content_style = self.CONTENT_STYLES[0]
        elif content_style not in self.CONTENT_STYLES:
            Trace.log("Entity", 0, "DialogWindow.run - wrong content style {!r}, available: {}".format(content_style, self.CONTENT_STYLES))
            content_style = self.CONTENT_STYLES[0]

        tc_dialog_window = TaskManager.createTaskChain()
        self.__tcs.append(tc_dialog_window)

        with tc_dialog_window as tc:
            tc.addSemaphore(self.__wait, From=False, To=True)
            tc.addFunction(Log, "  start run")
            tc.addFunction(self.__changeTexts, text_ids, text_args)
            tc.addFunction(self.__attachContentMovie, content_style)
            tc.addFunction(self.__setupUrls, urls)
            tc.addFunction(self.__attachContentIcon, icon_obj)

            with tc.addParallelTask(2) as (tc_show, tc_fade):
                tc_show.addScope(self.scopeOpenWindow)
                tc_fade.addTask("AliasFadeIn", FadeGroupName="FadeUI", To=0.5, Time=250.0, ReturnItem=False)

            with tc.addRepeatTask() as (repeat, until):
                repeat.addScope(self.scopeClickUrls)
                until.addScope(self.scopeRaceClickButtons)

            with tc.addParallelTask(2) as (tc_close, tc_fade):
                tc_close.addScope(self.scopeCloseWindow)
                tc_fade.addTask("AliasFadeOut", FadeGroupName="FadeUI", From=0.5, Time=250.0)

            tc.addFunction(self.__deattachContentMovie)
            tc.addFunction(self.__deattachIcon, icon_obj)
            tc.addFunction(Log, "  end run")
            tc.addSemaphore(self.__wait, To=False)

    def setButtonBlock(self, state, movie_name):
        movie = self.content.get(movie_name)
        if movie is None:
            Trace.log("Entity", 0, "DialogWindow.setButtonBlock: not found movie with name {!r}".format(movie_name))
            return

        movie.setBlock(state)

    # Custom presets ///////////////////////////////////////////////////////////////////////////////////////////////////

    def runPreset(self, preset_id, content_style=None, urls=None, text_args=None, icon_obj=None):
        text_ids = DialogWindowManager.getPreset(preset_id)

        if text_ids is None:
            Trace.log("Entity", 0, "DialogWindow.runPreset: not found preset with id '%s'" % preset_id)
            return

        self.run(content_style, text_ids, urls, text_args, icon_obj)
