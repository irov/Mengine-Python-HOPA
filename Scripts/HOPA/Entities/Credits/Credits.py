from Foundation.DefaultManager import DefaultManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockMusicVolumeFade import GuardBlockMusicVolumeFade
from Foundation.Notificator import Notificator
from Foundation.TaskManager import TaskManager
from Foundation.Utils import isCollectorEdition, setEnableLayer
from HOPA.TransitionManager import TransitionManager


CE_LABEL_LAYER = "ce_label"


class Credits(BaseEntity):

    def __init__(self):
        super(Credits, self).__init__()
        self.tc = None
        self.movie = None

        self.music_fade_cut_scene = DefaultManager.getDefault("MusicFadeCutScene", 0.25)

        self.button_link_1 = None
        self.button_link_2 = None
        self.url_link_1 = None
        self.url_link_2 = None

        self.tc_button_link_1 = None
        self.tc_button_link_2 = None

    def _onPreparation(self):
        super(Credits, self)._onPreparation()

        self.movie = self.object.generateObject("Movie2_Credits", "Movie2_Credits")

        # COLLECTOR EDITION LOGO RESOLVE
        if self.movie.getResourceMovie().hasCompositionLayer("Credits", CE_LABEL_LAYER):
            setEnableLayer(isCollectorEdition(), CE_LABEL_LAYER, self.movie)

        if self.object.Group.hasObject('Movie2Button_ButtonLink1'):
            self.button_link_1 = self.object.Group.getObject("Movie2Button_ButtonLink1")
            self.url_link_1 = Mengine.getGameParamUnicode("CreditsLink1")
            if self.url_link_1 is None:
                Trace.log("Entity", 0, "Credits Link 1 is not found. Please set it in Configs.ini (CreditsLink1)")
                self.button_link_1.setBlock(True)

        if self.object.Group.hasObject('Movie2Button_ButtonLink2'):
            self.button_link_2 = self.object.Group.getObject("Movie2Button_ButtonLink2")
            self.url_link_2 = Mengine.getGameParamUnicode("CreditsLink2")
            if self.url_link_2 is None:
                Trace.log("Entity", 0, "Credits Link 2 is not found. Please set it in Configs.ini (CreditsLink2)")
                self.button_link_2.setBlock(True)

    def _onActivate(self):
        super(Credits, self)._onActivate()

        self.tc = TaskManager.createTaskChain(Repeat=False)

        with self.tc as source:
            with GuardBlockMusicVolumeFade(source, "CutScene", self.music_fade_cut_scene) as tc:
                with tc.addRaceTask(2) as (tc_skip, tc_movie_play):
                    tc_skip.addTask('TaskMovie2ButtonClick', GroupName="Credits", Movie2ButtonName='Movie2Button_Next')
                    tc_movie_play.addScope(self._scopePlayCredits)

                tc.addFunction(TransitionManager.changeScene, "Menu")
                tc.addNotify(Notificator.onMusicPlatlistPlay, "Playlist_Menu")

        if self.button_link_1 is not None and self.url_link_1 is not None:
            self.tc_button_link_1 = TaskManager.createTaskChain(Repeat=True)
            with self.tc_button_link_1 as tc:
                tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_link_1)
                tc.addFunction(Mengine.openUrlInDefaultBrowser, self.url_link_1)

        if self.button_link_2 is not None and self.url_link_2 is not None:
            self.tc_button_link_2 = TaskManager.createTaskChain(Repeat=True)
            with self.tc_button_link_2 as tc:
                tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_link_2)
                tc.addFunction(Mengine.openUrlInDefaultBrowser, self.url_link_2)

    def _scopePlayCredits(self, source):
        animation = self.movie.entity.getAnimation()
        pressed_speed = DefaultManager.getDefaultFloat("DefaultCreditPressedScrollSpeed", 5.0)

        def _updateSpeedFactor(source, speed):
            time = animation.getTime()
            source.addTask("TaskMovie2Play", Movie2=self.movie, StartTiming=time, SpeedFactor=speed,
                           DefaultSpeedFactor=1.0, Wait=False)

        event_credits_done = Event("onCreditsDone")

        with source.addParallelTask(2) as (play, speed):
            play.addTask("TaskMovie2Play", Movie2=self.movie, Wait=True)
            play.addFunction(event_credits_done)

            with speed.addRepeatTask() as (repeat, until):
                repeat.addTask("TaskMouseButtonClick", isDown=True)
                repeat.addScope(_updateSpeedFactor, pressed_speed)
                repeat.addTask("TaskMouseButtonClick", isDown=False)
                repeat.addScope(_updateSpeedFactor, 1.0)

                until.addEvent(event_credits_done)

    def _onDeactivate(self):
        if self.tc is not None:
            self.tc.cancel()

        if self.movie is not None:
            self.movie.onDestroy()
            self.movie = None

        if self.tc_button_link_1 is not None:
            self.tc_button_link_1.cancel()
            self.tc_button_link_1 = None

        if self.tc_button_link_2 is not None:
            self.tc_button_link_2.cancel()
            self.tc_button_link_2 = None
