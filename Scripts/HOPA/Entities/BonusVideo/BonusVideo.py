from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GroupManager import GroupManager
from Foundation.TaskManager import TaskManager
from HOPA.BonusManager import BonusManager
from HOPA.BonusVideoManager import BonusVideoManager


class Page(object):
    def __init__(self, movie, bg_id=None, cut_scene_name=None):
        self.id = bg_id
        self.movie = movie
        self.cut_scene_name = cut_scene_name
        self.isBlock = False


class PageBlock(Page):
    def __init__(self, movie):
        super(PageBlock, self).__init__(movie)
        self.isBlock = True


class BonusVideo(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addAction("CurrentPageIndex")

    def __init__(self):
        super(BonusVideo, self).__init__()
        self.pages = []
        self.all_videos = None

        self.next_video_button = None
        self.pre_video_button = None
        self.set_video_button = None

        self.current_page = None

        self.tc = None

    def _onPreparation(self):
        switch_buttons = BonusManager.getStates()
        for button in switch_buttons.values():
            GroupManager.getObject('Bonus', button.button_name).setBlock(False)

        button_video = GroupManager.getObject('Bonus', 'Movie2Button_BonusVideo')
        button_video.setBlock(True)

        self.all_videos = BonusVideoManager.getVideos()
        self.__setupVideos()

        self.next_video_button = self.object.getObject("Movie2Button_NextVideo")
        self.pre_video_button = self.object.getObject("Movie2Button_PreVideo")
        self.set_video_button = self.object.getObject("Movie2Button_SetVideo")

        self.current_page = self.pages[self.CurrentPageIndex]
        self.current_page.movie.setEnable(True)

    def _onDeactivate(self):
        self.__cleanUp()

    def __cleanUp(self):
        if self.tc is not None:
            self.tc.cancel()
        self.tc = None

        for page in self.pages:
            page.movie.setEnable(False)

        self.pages = []
        self.all_videos = None

        self.next_video_button = None
        self.pre_video_button = None
        self.set_video_button = None

        self.current_page = None

    def _onActivate(self):
        self.tc = TaskManager.createTaskChain(Repeat=True)

        with self.tc as tc:
            with tc.addRaceTask(2) as (tc_scroll, tc_play):
                with tc_scroll.addRaceTask(2) as (tc1, tc2):
                    tc1.addTask("TaskMovie2ButtonClick", Movie2Button=self.next_video_button)
                    tc1.addScope(self.__scopeSwitchButtonClick, 1)

                    tc2.addTask("TaskMovie2ButtonClick", Movie2Button=self.pre_video_button)
                    tc2.addScope(self.__scopeSwitchButtonClick, -1)

                tc_play.addTask("TaskMovie2ButtonClick", Movie2Button=self.set_video_button)
                tc_play.addFunction(self.__tryPlayCutScene)

    def __scopeChangeWallPaper(self, source, old_page, new_page):
        if old_page == new_page:
            return

        with source.addParallelTask(2) as (source_old, source_new):
            source_old.addTask("AliasObjectAlphaTo", Object=old_page, Time=500, From=1.0, To=0.0, Wait=True)
            source_old.addDisable(old_page)

            source_new.addEnable(new_page)
            source_new.addTask("AliasObjectAlphaTo", Object=new_page, Time=500, From=0.0, To=1.0, Wait=True)

    def __setupVideos(self):
        for video_id, video_param in self.all_videos.iteritems():
            movie = self.object.getObject(video_param.bgName)
            movie.setEnable(False)
            if video_param.isReceived is False:
                continue

            bg_state = Page(movie, video_id, video_param.cutSceneName)
            self.pages.append(bg_state)

        if BonusVideoManager.getCounterReceivedVideos() >= len(self.all_videos):
            return

        if len(self.pages) == 0:
            movie = self.object.getObject('Movie2_BlockedVideo')
            self.__handleBlockedVideoText(movie, "ID_BONUSVIDEO_BLOCKED")
            bg_state_block = PageBlock(movie)
            self.pages.append(bg_state_block)

    def __handleBlockedVideoText(self, movie, text_id):
        if movie.hasMovieText(text_id) is False:
            return
        if Mengine.existText(text_id) is True:
            return

        text = movie.getMovieText(text_id)
        text.disable()
        if _DEVELOPMENT is True:
            Trace.msg("[!] {} has text '{}' but it isn't registered in current locale '{}'".format(movie.getName(), text.getName(), Mengine.getLocale()))

    def __scopeSwitchButtonClick(self, source, value):
        old_page_index = self.CurrentPageIndex
        new_page_index = (self.CurrentPageIndex + value) % len(self.pages)

        old_page_movie = self.pages[old_page_index].movie
        new_page_movie = self.pages[new_page_index].movie

        self.object.setParam('CurrentPageIndex', new_page_index)
        self.current_page = self.pages[self.CurrentPageIndex]
        source.addScope(self.__scopeChangeWallPaper, old_page_movie, new_page_movie)

    def __tryPlayCutScene(self):
        if self.current_page.isBlock is True:
            return

        cut_scene_name = self.current_page.cut_scene_name
        Notification.notify(Notificator.onBonusCutScenePlay, cut_scene_name)
