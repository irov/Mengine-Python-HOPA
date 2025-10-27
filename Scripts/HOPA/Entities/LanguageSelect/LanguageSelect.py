from Event import Event
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.Entities.Options.Options import Options
from HOPA.LanguageSelectManager import LanguageSelectManager, LanguageSelectParam
from HOPA.ZoomManager import ZoomManager


class LanguageSelect(BaseEntity):
    EVENT_CHANGE_LANG = Event('ButtonLangSelected')

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction("bPrevLangSetted")
        Type.addAction("PrevLanguage")

    def __init__(self):
        super(LanguageSelect, self).__init__()

        self.buttons = {}

        self.tc_ok = None
        self.tc_cancel = None
        self.tc_change_lang = None
        self.tcs_buttons = []

    def _onPreparation(self):
        slot_index = LanguageSelectParam.slot_index_begin

        for param in LanguageSelectManager.getParams():
            movie_slot_holder, button_prototype, alias, alias_over, text, text_over, lang = param.get()

            if not Mengine.hasLocale(lang):  # exclude language that currently not in project
                continue

            slot_name = LanguageSelectParam.getSlotFormat(slot_index)

            parent_movie = self.object.getObject(movie_slot_holder)

            button = self.object.tryGenerateObjectUnique(button_prototype + slot_name, button_prototype, Enable=True)

            slot_in_slots_movie = parent_movie.getMovieSlot(slot_name)
            if slot_in_slots_movie is None:
                Trace.log("Entity", 0, "[LanguageSelect] movie: %s not found slot: %s for lang: %s" % (parent_movie.name, slot_name, lang))
                continue

            slot_in_slots_movie.addChild(button.getEntityNode())

            if Mengine.getLocale() == lang:
                button.setBlock(True)  # highlight current language

            for movie in button.eachMovies():  # setup texts
                movie.setTextAliasEnvironment(slot_name)
                if movie.entity.hasMovieText(alias):
                    Mengine.setTextAlias(slot_name, alias, text)

                elif movie.entity.hasMovieText(alias_over):
                    Mengine.setTextAlias(slot_name, alias_over, text_over)

                else:
                    Trace.log("Entity", 0, "[LanguageSelect] button movie state '%s' should have '%s' or '%s' text aliases" % (movie.name, alias, alias_over))

            self.buttons[lang] = button

            slot_index += 1

    def setOptionsStarVolumeValues(self, volume_values):
        Options.setStartVolumeValues(volume_values[0], volume_values[1], volume_values[2])

    @staticmethod
    def __setLanguage(scene_name, lang):
        if SceneManager.getCurrentScene() is not None:
            SceneManager.disableCurrentScene()

        def cbOnSceneRestartChangeLocale(scene, isActive, isError):  # CB for actual changing game localization
            if scene is None:
                Mengine.setLocale(lang)  # set locale can only work when current scene is None

        Mengine.restartCurrentScene(True, cbOnSceneRestartChangeLocale)

    def __handleLanguageChange(self, lang):
        if lang is None or str(Mengine.getLocale()) == lang:
            return

        with TaskManager.createTaskChain() as tc:
            with GuardBlockInput(tc) as guard_tc:
                # close zoom
                with guard_tc.addIfTask(lambda: ZoomManager.getZoomOpenGroupName() is not None) as (true, _):
                    true.addFunction(lambda: ZoomManager.closeZoom(ZoomManager.getZoomOpenGroupName()))
                    true.addListener(Notificator.onZoomEmpty)

                scene_name = SceneManager.getCurrentSceneName()

                guard_tc.addFunction(self.__setLanguage, scene_name, lang)
                # Need to proper scene restart
                guard_tc.addTask("AliasTransition", SceneName=scene_name, CheckToScene=False, Fade=False)
                guard_tc.addTask("AliasFadeIn", FadeGroupName='FadeUI', To=0.5, Time=250.0)
                guard_tc.addTask('TaskSceneLayerGroupEnable', LayerName='LanguageSelect', Value=True)
                guard_tc.addScope(self.scopeOpen, "LanguageSelect")

    def __onLangButtonClicked(self, lang):
        if not self.object.getParam("bPrevLangSetted"):
            self.object.setParam("bPrevLangSetted", True)
            self.object.setParam("PrevLanguage", Mengine.getLocale())

        self.__handleLanguageChange(lang)
        return False

    def __onOkButtonClicked(self):
        self.object.setParam("bPrevLangSetted", False)
        self.object.setParam("PrevLanguage", None)

        if SystemManager.hasSystem("SystemOptions"):
            SystemManager.getSystem("SystemOptions").language = Mengine.getLocale()

        if SystemManager.hasSystem("SystemAutoLanguage"):
            SystemManager.getSystem("SystemAutoLanguage").disable()

    def __onCancelButtonClicked(self):
        if self.object.getParam("bPrevLangSetted"):
            self.__handleLanguageChange(self.object.getParam("PrevLanguage"))

    def _onActivate(self):
        # TC Change Language On Button Click Listener
        self.tc_change_lang = TaskManager.createTaskChain(Repeat=True, Name='LanguageSelect_LangButtonClick_Listener')
        with self.tc_change_lang as tc:
            tc.addEvent(self.EVENT_CHANGE_LANG, self.__onLangButtonClicked)  # handle lang button click

        # TC Lang Button Click Notify
        for (lang, button) in self.buttons.iteritems():
            tc_button = TaskManager.createTaskChain(Repeat=True, Name='LanguageSelect_LangButtonClick_%s_Notifiy' % button.name)
            self.tcs_buttons.append(tc_button)

            with tc_button as tc:
                tc.addTask("TaskMovie2ButtonClick", Movie2Button=button)
                tc.addFunction(self.EVENT_CHANGE_LANG, lang)

        self.tc_ok = TaskManager.createTaskChain(Name='LanguageSelect_Ok')
        self.tc_cancel = TaskManager.createTaskChain(Name='LanguageSelect_Cancel')
        if GroupManager.hasObject('LanguageSelect', 'Movie2_SocketClose') is True:
            self.tc_click_out = TaskManager.createTaskChain(Name='LanguageSelect_Click_Out')

        # TC OK Button Click
        with self.tc_ok as tc:
            tc.addTask('TaskMovie2ButtonClick', GroupName='LanguageSelect', Movie2ButtonName='Movie2Button_OK')
            tc.addFunction(self.tc_cancel.cancel)

            # handle ok button click
            tc.addFunction(self.__onOkButtonClicked)

            # close ui
            tc.addScope(self.scopeClose, "LanguageSelect")
            tc.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            volume_values = Options.getStartVolumeValues()
            tc.addScope(self.scopeOpen, "Options")
            tc.addFunction(self.setOptionsStarVolumeValues, volume_values)
            tc.addTask('TaskSceneLayerGroupEnable', LayerName='LanguageSelect', Value=False)

        # TC Cancel Button click
        with self.tc_cancel as tc:
            tc.addTask('TaskMovie2ButtonClick', GroupName='LanguageSelect', Movie2ButtonName='Movie2Button_Cancel')
            tc.addFunction(self.tc_ok.cancel)

            tc.addScope(self._scopeHandleCancelClick)

        # TC Cancel Socket click
        if GroupManager.hasObject('LanguageSelect', 'Movie2_SocketClose') is True:
            with self.tc_click_out as tc:
                tc.addTask('TaskMovie2SocketClick', GroupName='LanguageSelect',
                           Movie2Name='Movie2_SocketClose', SocketName="close")
                tc.addFunction(self.tc_ok.cancel)
                tc.addFunction(self.tc_cancel.cancel)

                tc.addScope(self._scopeHandleCancelClick)

    def _scopeHandleCancelClick(self, source):
        def _filter():
            return self.object.getParam("bPrevLangSetted") and self.object.getParam("PrevLanguage") != Mengine.getLocale()

        with source.addIfTask(_filter) as (tc_true, tc_false):
            # handle cancel click
            tc_true.addFunction(self.__onCancelButtonClicked)

            # close ui
            tc_false.addScope(self.scopeClose, "LanguageSelect")
            tc_false.addTask("TaskSceneLayerGroupEnable", LayerName="Options", Value=True)
            volume_values = Options.getStartVolumeValues()
            tc_false.addScope(self.scopeOpen, "Options")
            tc_false.addFunction(self.setOptionsStarVolumeValues, volume_values)
            tc_false.addTask('TaskSceneLayerGroupEnable', LayerName='LanguageSelect', Value=False)

    def _onDeactivate(self):
        if self.tc_ok is not None:
            self.tc_ok.cancel()
            self.tc_ok = None

        if self.tc_cancel is not None:
            self.tc_cancel.cancel()
            self.tc_cancel = None

        if self.tc_change_lang is not None:
            self.tc_change_lang.cancel()
            self.tc_change_lang = None

        if self.tc_click_out is not None:
            self.tc_click_out.cancel()
            self.tc_click_out = None

        for tc_button in self.tcs_buttons:
            tc_button.cancel()
        self.tcs_buttons = []

        for button in self.buttons.values():
            button.onDestroy()

    ''' Scene FX '''

    def scopeOpen(self, source, GroupName):
        source.addScope(self.sceneEffect, GroupName, "Movie2_Open")

    def scopeClose(self, source, GroupName):
        source.addScope(self.sceneEffect, GroupName, "Movie2_Close")

    @staticmethod
    def sceneEffect(source, GroupName, MovieName):
        if GroupManager.hasObject(GroupName, MovieName) is True:
            if not GroupManager.getGroup(GroupName).getEnable():
                source.addDummy()
                return

            Movie = GroupManager.getObject(GroupName, MovieName)
            with GuardBlockInput(source) as guard_source:
                guard_source.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, AutoEnable=True)

    ''' Scene FX '''
