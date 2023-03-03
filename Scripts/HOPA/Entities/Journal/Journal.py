from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.ObjectManager import ObjectManager
from Foundation.SceneManager import SceneManager
from Foundation.TaskManager import TaskManager
from HOPA.JournalManager import JournalManager


TEXT_ID_PAGE_NUMBER = "ID_JOURNAL_PAGE_NUMBER"

TEXT_ALIAS_ENV = ""

TEXT_ALIAS_LEFT_PAGE_NUMBER = "$JournalLeftPageNumber"
TEXT_ALIAS_RIGHT_PAGE_NUMBER = "$JournalRightPageNumber"

TEXT_ALIAS_OLD_LEFT_PAGE_NUMBER = "$OldJournalLeftPageNumber"
TEXT_ALIAS_OLD_RIGHT_PAGE_NUMBER = "$OldJournalRightPageNumber"

TEXT_ALIAS_NEW_LEFT_PAGE_NUMBER = "$NewJournalLeftPageNumber"
TEXT_ALIAS_NEW_RIGHT_PAGE_NUMBER = "$NewJournalRightPageNumber"


class Journal(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addAction(Type, "Pages", Append=Journal.__cbAppendPage)
        Type.addAction(Type, "CurrentPage")

    def __cbAppendPage(self, page_index, page_id):
        Notification.notify(Notificator.onBonusVideoOpenCutScene, page_id)
        return False

    def __init__(self):
        super(Journal, self).__init__()

        self.tc = None

        self.group_page = None

        self.socket_back = None
        self.socket_close = None

        self.button_left = None
        self.button_right = None
        self.button_play = None

        self.movie_move_right = None
        self.movie_move_left = None
        self.movie_move_idle = None

        self.movie_bg = None

        self.time_effect = DefaultManager.getDefaultFloat("DefaultJournalPageAlphaTime", 300.0)
        self.skip_speed_factor = DefaultManager.getDefaultFloat("DefaultJournalPageSkipSpeedFactor", 3.0)

    def __resetPageNumbers(self):
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_LEFT_PAGE_NUMBER, " ")
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_RIGHT_PAGE_NUMBER, " ")
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_OLD_LEFT_PAGE_NUMBER, " ")
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_OLD_RIGHT_PAGE_NUMBER, " ")
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_NEW_LEFT_PAGE_NUMBER, " ")
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_NEW_RIGHT_PAGE_NUMBER, " ")

    def _onPreparation(self):
        super(Journal, self)._onPreparation()

        button_left_candidates = ["Button_Left", "Movie2Button_Left", ]
        for button_left_name in button_left_candidates:
            if self.object.hasObject(button_left_name):
                self.button_left = self.object.getObject(button_left_name)
                break
        self.button_left.setEnable(False)

        button_right_candidates = ["Button_Right", "Movie2Button_Right", ]
        for button_right_name in button_right_candidates:
            if self.object.hasObject(button_right_name):
                self.button_right = self.object.getObject(button_right_name)
                break
        self.button_right.setEnable(False)

        if self.object.hasObject("Socket_Back"):
            self.socket_back = self.object.getObject("Socket_Back")
            self.socket_back.setInteractive(True)  # for block clicks

        if self.object.hasObject("Movie2Button_Play"):
            self.button_play = self.object.getObject("Movie2Button_Play")
            self.button_play.setEnable(False)

        if self.object.hasObject("Movie2_MoveLeft"):
            self.movie_move_left = self.object.getObject("Movie2_MoveLeft")

        if self.object.hasObject("Movie2_MoveRight"):
            self.movie_move_right = self.object.getObject("Movie2_MoveRight")

        if self.object.hasObject("Movie2_MoveIdle"):
            self.movie_move_idle = self.object.getObject("Movie2_MoveIdle")
            self.movie_move_idle.setEnable(True)

        if self.object.hasObject("Socket_Close"):
            self.socket_close = self.object.getObject("Socket_Close")

        if self.object.hasObject("Movie2_Bg"):
            self.movie_bg = self.object.getObject("Movie2_Bg")
            self.movie_bg.setInteractive(True)  # for socket Block
            self.socket_close = self.movie_bg.getSocket("close")

        Mengine.setTextAlias(TEXT_ALIAS_ENV, TEXT_ALIAS_LEFT_PAGE_NUMBER, TEXT_ID_PAGE_NUMBER)
        Mengine.setTextAlias(TEXT_ALIAS_ENV, TEXT_ALIAS_RIGHT_PAGE_NUMBER, TEXT_ID_PAGE_NUMBER)
        Mengine.setTextAlias(TEXT_ALIAS_ENV, TEXT_ALIAS_OLD_LEFT_PAGE_NUMBER, TEXT_ID_PAGE_NUMBER)
        Mengine.setTextAlias(TEXT_ALIAS_ENV, TEXT_ALIAS_OLD_RIGHT_PAGE_NUMBER, TEXT_ID_PAGE_NUMBER)
        Mengine.setTextAlias(TEXT_ALIAS_ENV, TEXT_ALIAS_NEW_LEFT_PAGE_NUMBER, TEXT_ID_PAGE_NUMBER)
        Mengine.setTextAlias(TEXT_ALIAS_ENV, TEXT_ALIAS_NEW_RIGHT_PAGE_NUMBER, TEXT_ID_PAGE_NUMBER)

        self.__resetPageNumbers()

    def __scopeUpdateButtonsMove(self, source):
        if self.CurrentPage is None:
            return

        current_index = self.Pages.index(self.CurrentPage)

        with source.addParallelTask(2) as (source_btn_left, source_btn_right):
            if current_index > 0:
                if self.button_left.getEnable() is False:
                    source_btn_left.addEnable(self.button_left)
                    source_btn_left.addTask("AliasObjectAlphaTo", Object=self.button_left,
                                            Time=self.time_effect, From=0.0, To=1.0)
            else:
                if self.button_left.getEnable() is True:
                    source_btn_left.addTask("AliasObjectAlphaTo", Object=self.button_left,
                                            Time=self.time_effect, From=1.0, To=0.0)
                    source_btn_left.addDisable(self.button_left)

            if current_index + 1 < len(self.Pages):
                if self.button_right.getEnable() is False:
                    source_btn_right.addEnable(self.button_right)
                    source_btn_right.addTask("AliasObjectAlphaTo", Object=self.button_right,
                                             Time=self.time_effect, From=0.0, To=1.0)
            else:
                if self.button_right.getEnable() is True:
                    source_btn_right.addTask("AliasObjectAlphaTo", Object=self.button_right,
                                             Time=self.time_effect, From=1.0, To=0.0)
                    source_btn_right.addDisable(self.button_right)

    def __updateButtonsMove(self):
        if self.CurrentPage is None:
            return

        current_index = self.Pages.index(self.CurrentPage)

        if current_index > 0:
            self.button_left.setEnable(True)
        else:
            self.button_left.setEnable(False)

        if current_index + 1 < len(self.Pages):
            self.button_right.setEnable(True)
        else:
            self.button_right.setEnable(False)

        self.button_left.setAlpha(1.0)
        self.button_right.setAlpha(1.0)

    def __updateButtonPlay(self, page):
        if page is None:
            return
        if self.button_play is None:
            return

        if page.cutScene is None:
            self.button_play.setEnable(False)
        else:
            self.button_play.setEnable(True)

    def __getNewPage(self, button):
        if button == self.button_left:
            offset = -1
        elif button == self.button_right:
            offset = 1
        else:
            return None

        current_index = self.Pages.index(self.CurrentPage)
        new_page_index = current_index + offset

        return self.Pages[new_page_index]

    def __getPageNumbers(self, page_name):
        page_index = self.Pages.index(page_name)

        left_page_number = page_index * 2 + 1
        right_page_number = page_index * 2 + 2

        return left_page_number, right_page_number

    def __setupPageText(self):
        current_page_desc = JournalManager.getJournalPage(self.CurrentPage)
        for index, textID in enumerate(current_page_desc.textIDs):
            object_text = self.group_page.getObject("Text_Message{}".format(index))
            object_text.setParam("TextID", textID)

    def __loadPage(self):
        if self.group_page is not None:
            self.group_page.onDisable()
            self.group_page = None

        if self.CurrentPage is None:
            return

        current_page_desc = JournalManager.getJournalPage(self.CurrentPage)
        self.__updateButtonPlay(current_page_desc)

        current_scene_name = SceneManager.getCurrentSceneName()
        self.group_page = SceneManager.getSceneLayerGroup(current_scene_name, current_page_desc.groupName)

        if self.group_page.getEnable() is False:
            self.group_page.onEnable()

        group_layer = self.group_page.getMainLayer()

        if self.movie_move_idle:
            slot_idle_left_page = self.movie_move_idle.getMovieSlot("left_page")
            slot_idle_right_page = self.movie_move_idle.getMovieSlot("right_page")

            layer_new_left_page = group_layer
            layer_new_right_page = self.group_page.getLayer("Layer2D_RightPage")

            slot_idle_left_page.addChild(layer_new_left_page)
            if layer_new_right_page:
                slot_idle_right_page.addChild(layer_new_right_page)

            if self.button_play:
                button_play_entity_node = self.button_play.getEntityNode()
                slot_idle_right_page.addChild(button_play_entity_node)
        else:
            self.node.addChild(group_layer)

        # setup page numbers
        current_left_page_number, current_right_page_number = self.__getPageNumbers(self.CurrentPage)

        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_LEFT_PAGE_NUMBER, current_left_page_number)
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_RIGHT_PAGE_NUMBER, current_right_page_number)

        self.__setupPageText()
        self.__updateButtonsMove()

    def __policyScopeClickSocket(self, source, socket, holder=None):
        if socket:
            source.addTask("TaskSocketClick", Socket=socket)
            if holder:
                source.addFunction(holder.set, socket)
        else:
            source.addBlock()

    def __policyScopeClickHotSpotPolygon(self, source, socket, holder=None):
        if socket:
            source.addTask("TaskNodeSocketClick", Socket=socket)
            if holder:
                source.addFunction(holder.set, socket)
        else:
            source.addBlock()

    def __policyScopeClickButton(self, source, button, holder=None):
        if button:
            source.addTask("TaskButtonClick", Button=button)
            if holder:
                source.addFunction(holder.set, button)
        else:
            source.addBlock()

    def __policyScopeClickMovie2Button(self, source, button, holder=None):
        if button:
            source.addTask("TaskMovie2ButtonClick", Movie2Button=button)
            if holder:
                source.addFunction(holder.set, button)
        else:
            source.addBlock()

    def __scopePageSwitch(self, source, page_old_name, page_new_name):
        page_old = JournalManager.getJournalPage(page_old_name)
        page_new = JournalManager.getJournalPage(page_new_name)

        current_scene_name = SceneManager.getCurrentSceneName()
        group_old = SceneManager.getSceneLayerGroup(current_scene_name, page_old.groupName)
        group_new = SceneManager.getSceneLayerGroup(current_scene_name, page_new.groupName)

        layer_group_old = group_old.getMainLayer()
        layer_group_new = group_new.getMainLayer()

        self.node.addChild(layer_group_old)
        self.node.addChild(layer_group_new)

        with source.addParallelTask(2) as (tc_buttons, tc_effect):
            tc_buttons.addScope(self.__scopeUpdateButtonsMove)

            with tc_effect.addParallelTask(3) as (tc_hide, tc_show, tc_btn):
                tc_hide.addTask("TaskNodeAlphaTo", Node=layer_group_old, Time=self.time_effect, From=1.0, To=0.0)

                tc_show.addTask("TaskNodeAlphaTo", Node=layer_group_new, Time=self.time_effect, From=0.0, To=1.0)

                if self.button_play:
                    if page_old.cutScene is not None and page_new.cutScene is None:
                        if self.button_play.getEnable() is True:
                            tc_btn.addTask("AliasObjectAlphaTo", Object=self.button_play,
                                           Time=self.time_effect, From=1.0, To=0.0)

                            tc_btn.addDisable(self.button_play)
                    elif page_old.cutScene is None and page_new.cutScene is not None:
                        if self.button_play.getEnable() is False:
                            tc_btn.addEnable(self.button_play)
                            tc_btn.addTask("AliasObjectAlphaTo", Object=self.button_play,
                                           Time=self.time_effect, From=0.0, To=1.0)

        source.addFunction(self.node.removeChild, layer_group_old)

    def __scopeSkipPageSwitch(self, source):
        with source.addRaceTask(2) as (source_btn_left, source_btn_right):
            source_btn_left.addScope(self.__scopeClickObject, self.button_left)
            source_btn_right.addScope(self.__scopeClickObject, self.button_right)

    def __scopePlayMovieWithLastFrameSkip(self, source, movie, scope_skip):
        sem_skip = Semaphore(False, "Skip")

        with source.addRaceTask(2) as (source_play, source_skip):
            source_play.addPlay(movie)

            source_skip.addScope(scope_skip)
            source_skip.addSemaphore(sem_skip, To=True)

        with source.addIfSemaphore(sem_skip, True) as (source_true, source_false):
            source_true.addParam(movie, "LastFrame", True)

    def __scopePlayMovieWithSpeedFactorSkip(self, source, movie, scope_skip):
        sem_skip = Semaphore(False, "Skip")
        timing_holder = Holder(0.0)

        def __prepare(holder, movie_object):
            entity = movie_object.getEntity()
            movie_node = entity.getMovie()

            animation = movie_node.getAnimation()
            timing = animation.getTime()

            holder.set(timing)

        def __setup(holder, movie_object):
            timing = holder.get()
            movie_object.setParam("StartTiming", timing)
            movie_object.setParam("SpeedFactor", self.skip_speed_factor)

        def __restore(movie_object):
            movie_object.setParam("StartTiming", 0.0)
            movie_object.setParam("SpeedFactor", 1.0)

        with source.addRaceTask(2) as (source_play, source_skip):
            source_play.addPlay(movie)

            source_skip.addScope(scope_skip)

            source_skip.addFunction(__prepare, timing_holder, movie)
            source_skip.addSemaphore(sem_skip, To=True)

        with source.addIfSemaphore(sem_skip, True) as (source_true, source_false):
            source_true.addFunction(__setup, timing_holder, movie)
            source_true.addPlay(movie)
            source_true.addFunction(__restore, movie)

    def __scopePageSwitchWithMove(self, source, page_old_name, page_new_name, movie_move):
        page_old = JournalManager.getJournalPage(page_old_name)
        page_new = JournalManager.getJournalPage(page_new_name)

        self.__resetPageNumbers()

        old_left_page_number, old_right_page_number = self.__getPageNumbers(page_old_name)

        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_OLD_LEFT_PAGE_NUMBER, old_left_page_number)
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_OLD_RIGHT_PAGE_NUMBER, old_right_page_number)

        new_left_page_number, new_right_page_number = self.__getPageNumbers(page_new_name)

        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_NEW_LEFT_PAGE_NUMBER, new_left_page_number)
        Mengine.setTextAliasArguments(TEXT_ALIAS_ENV, TEXT_ALIAS_NEW_RIGHT_PAGE_NUMBER, new_right_page_number)

        current_scene_name = SceneManager.getCurrentSceneName()
        group_old = SceneManager.getSceneLayerGroup(current_scene_name, page_old.groupName)
        group_new = SceneManager.getSceneLayerGroup(current_scene_name, page_new.groupName)

        layer_group_old = group_old.getMainLayer()
        layer_group_new = group_new.getMainLayer()

        slot_old_left_page = movie_move.getMovieSlot("old_left_page")
        slot_old_right_page = movie_move.getMovieSlot("old_right_page")
        slot_new_left_page = movie_move.getMovieSlot("new_left_page")
        slot_new_right_page = movie_move.getMovieSlot("new_right_page")

        layer_old_left_page = layer_group_old
        layer_old_right_page = group_old.getLayer("Layer2D_RightPage")

        slot_old_left_page.addChild(layer_old_left_page)
        if layer_old_right_page:
            slot_old_right_page.addChild(layer_old_right_page)

        layer_new_left_page = layer_group_new
        layer_new_right_page = group_new.getLayer("Layer2D_RightPage")

        slot_new_left_page.addChild(layer_new_left_page)
        if layer_new_right_page:
            slot_new_right_page.addChild(layer_new_right_page)

        old_movie_button_play = None
        new_movie_button_play = None

        if self.button_play:
            self.button_play.setEnable(False)

            resource_movie = Mengine.getResourceReference(self.button_play.getResourceMovie())
            composition_name = self.button_play.getCompositionNameIdle()

            if page_old.cutScene:
                old_movie_button_play = ObjectManager.createObjectUnique("Movie2", "Movie2_Button_Play_Old", None,
                                                                         ResourceMovie=resource_movie,
                                                                         CompositionName=composition_name)
                old_movie_button_play_node = old_movie_button_play.getEntityNode()
                slot_old_right_page.addChild(old_movie_button_play_node)

            if page_new.cutScene:
                new_movie_button_play = ObjectManager.createObjectUnique("Movie2", "Movie2_Button_Play_New", None,
                                                                         ResourceMovie=resource_movie,
                                                                         CompositionName=composition_name)

                new_movie_button_play_node = new_movie_button_play.getEntityNode()
                slot_new_right_page.addChild(new_movie_button_play_node)

        source.addEnable(movie_move)

        sem_play_end = Semaphore(False, "MovieMovePlayEnd")

        with source.addParallelTask(2) as (source_buttons, source_effect):
            with source_buttons.addRaceTask(2) as (source_job, source_skip):
                source_job.addScope(self.__scopeUpdateButtonsMove)
                source_skip.addSemaphore(sem_play_end, From=True)

            source_effect.addScope(self.__scopePlayMovieWithSpeedFactorSkip, movie_move, self.__scopeSkipPageSwitch)
            source_effect.addSemaphore(sem_play_end, To=True)

        if new_movie_button_play:
            source.addFunction(new_movie_button_play.onDestroy)
        if old_movie_button_play:
            source.addFunction(old_movie_button_play.onDestroy)

        if layer_old_right_page:
            source.addFunction(slot_old_right_page.removeChild, layer_old_right_page)
        source.addFunction(slot_old_left_page.removeChild, layer_old_left_page)
        source.addDisable(movie_move)

    def __scopeClickButtonMove(self, source, button):
        page_old_name = self.CurrentPage
        page_name_new = self.__getNewPage(button)

        page_new = JournalManager.getJournalPage(page_name_new)

        group_old = self.group_page

        current_scene_name = SceneManager.getCurrentSceneName()
        self.group_page = SceneManager.getSceneLayerGroup(current_scene_name, page_new.groupName)
        self.group_page.onEnable()

        # need at this position for correct move buttons update
        Notification.notify(Notificator.onJournalSetPage, page_name_new)

        movie_move = self.movie_move_left if button is self.button_left else self.movie_move_right

        self.__setupPageText()

        if movie_move and group_old is not self.group_page:
            source.addScope(self.__scopePageSwitchWithMove, page_old_name, page_name_new, movie_move)
        else:
            source.addScope(self.__scopePageSwitch, page_old_name, page_name_new)

        source.addFunction(group_old.onDisable)
        source.addFunction(self.__loadPage)

    def __scopeResolveClick(self, source, holder):
        object_click = holder.get()

        if object_click is None:
            source.addDummy()
        elif object_click is self.socket_close:
            source.addNotify(Notificator.onJournalClose)
        elif object_click is self.button_left:
            source.addScope(self.__scopeClickButtonMove, object_click)
        elif object_click is self.button_right:
            source.addScope(self.__scopeClickButtonMove, object_click)
        else:
            source.addDummy()

    def __getScopeClickObject(self, object_):
        if object_ is None:
            return

        object_type_ = object_.getType()

        click_policies = dict(ObjectSocket=self.__policyScopeClickSocket,
                              HotSpotPolygon=self.__policyScopeClickHotSpotPolygon,
                              ObjectButton=self.__policyScopeClickButton,
                              ObjectMovie2Button=self.__policyScopeClickMovie2Button)

        return click_policies.get(object_type_)

    def __scopeClickObject(self, source, object_, holder=None):
        scope_click_object = self.__getScopeClickObject(object_)

        if scope_click_object is None:
            source.addBlock()
            return

        source.addScope(scope_click_object, object_, holder)

    def __runTaskChain(self):
        tc_name = "Journal{}".format(id(self))

        self.tc = TaskManager.createTaskChain(Name=tc_name, Repeat=True)

        holder_click_object = Holder()

        with self.tc as source:
            with source.addRaceTask(3) as (tc_socket_close, tc_btn_left, tc_btn_right):
                tc_socket_close.addScope(self.__scopeClickObject, self.socket_close, holder_click_object)
                tc_btn_left.addScope(self.__scopeClickObject, self.button_left, holder_click_object)
                tc_btn_right.addScope(self.__scopeClickObject, self.button_right, holder_click_object)

            with GuardBlockInput(source) as guard_source:
                guard_source.addScope(self.__scopeResolveClick, holder_click_object)

    def _onActivate(self):
        super(Journal, self)._onActivate()
        self.__loadPage()

        self.__runTaskChain()

    def __cleanPage(self):
        if not self.group_page:
            return

        if self.group_page.getEnable() is False:
            self.group_page = None
            return

        group_layer = self.group_page.getMainLayer()
        group_layer.removeFromParent()

        if self.movie_move_idle:
            layer_new_right_page = self.group_page.getLayer("Layer2D_RightPage")
            if layer_new_right_page:
                layer_new_right_page.removeFromParent()

            if self.button_play:
                button_play_entity_node = self.button_play.getEntityNode()
                button_play_entity_node.removeFromParent()

        self.group_page.onDisable()
        self.group_page = None

    def __cleanUp(self):
        if self.tc:
            self.tc.cancel()
            self.tc = None

        self.__cleanPage()

        if self.socket_back:
            self.socket_back.setInteractive(False)
            self.socket_back = None

        self.button_left = None
        self.button_right = None

        if self.group_page is not None:
            self.group_page.onDisable()
            self.group_page = None

    def onCloseJournal(self):
        self.__cleanPage()

    def _onDeactivate(self):
        super(Journal, self)._onDeactivate()
        self.__cleanUp()
