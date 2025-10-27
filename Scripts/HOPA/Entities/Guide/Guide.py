from Event import Event
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager
from HOPA.GuideManager import GuideManager
from HOPA.System.SystemGuide import SystemGuide
from HOPA.TransitionManager import TransitionManager
from Holder import Holder


DEFAULT_ALIAS_ENV = ''
TEXT_ID_GUIDE_PAGE_COUNT = 'ID_GUIDE_PAGE_COUNT'

NAV_BUTTON_BACK_NAME = 'Movie2Button_Back'
NAV_BUTTON_MENU_NAME = 'Movie2Button_Menu'
NAV_BUTTON_LEFT_NAME = 'Movie2Button_Left'
NAV_BUTTON_RIGHT_NAME = 'Movie2Button_Right'
NAV_BUTTON_COUNTER_MOVIE_NAME = 'Movie2_Counter'

GUIDE_PARAM = GuideManager.getGuideParams()

ZOOM_IN_MOVE_TO = Mengine.vec2f(*GUIDE_PARAM.pic_zoom_pos)
ZOOM_IN_SCALE_TO = Mengine.vec2f(*GUIDE_PARAM.pic_zoom_scale)
ZOOM_OUT_SCALE_TO = Mengine.vec2f(1.0, 1.0)
ZOOM_IN_OUT_TIME = GUIDE_PARAM.pic_zoom_time

EVENT_PREV_PAGE = Event('GuidePrevPage')
EVENT_PREV_PAGE_FB = Event('GuidePrevPageFeedback')

EVENT_NEXT_PAGE = Event('GuideNextPage')
EVENT_NEXT_PAGE_FB = Event('GuideNextPageFeedback')

EVENT_SWITCH_FOCUS = Event('GuideSwitchFocus')
EVENT_SWITCH_FOCUS_FB = Event('GuideSwitchFocusFeedback')

PAGE_PROTOTYPE_MOVIE_TEXT_ALIAS_PREFIX = '$AliasText'
PAGE_PROTOTYPE_MOVIE_PIC_SLOT_PREFIX = 'pic_'

ID_EMPTY_TEXT = "ID_EMPTY_TEXT"
ID_TEXT_PAGE_PROTOTYPE_404 = "ID_GUIDE_CHAPTER_404"


class Navigation(object):
    def __init__(self, demon_object, button_back, button_menu, button_left, button_right, page_counter):
        self.demon_object = demon_object

        self.button_back = button_back
        self.button_menu = button_menu
        self.button_left = button_left
        self.button_right = button_right

        self.page_counter = page_counter

        self.tc_send_event_prev_page = None
        self.tc_send_event_next_page = None
        self.tc_send_event_switch_focus = None

        self.tc_receive_events_feedback = None

        self.tc_leave_scene = None

        self.menu_obj = None
        self.chapter_obj = None
        self.focus = True

    def __setFocus(self, focus):
        self.focus = focus

    def getFocus(self):
        return self.focus

    def getFocusObj(self):
        if self.focus:
            return self.menu_obj
        else:
            return self.chapter_obj

    def updatePageCounter(self):
        current_page_number = self.getFocusObj().getFocusPageNumber()
        pages_number = self.getFocusObj().getPagesNumber()
        Mengine.setTextAliasArguments(DEFAULT_ALIAS_ENV, TEXT_ID_GUIDE_PAGE_COUNT,
                                      str(current_page_number), str(pages_number))

        self.button_right.setBlock(current_page_number == pages_number)
        self.button_left.setBlock(current_page_number == 1)
        self.page_counter.setEnable(pages_number > 1)

    def __eventFeedback(self, focus, focus_obj):
        if focus:
            self.menu_obj = focus_obj
        else:
            self.chapter_obj = focus_obj
        self.focus = focus
        self.button_menu.setBlock(focus)
        return True

    def __scopeSendEventPrevPage(self, source):
        source.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_left)
        source.addFunction(EVENT_PREV_PAGE, self.getFocus, self.getFocusObj)

    def __scopeSendEventNextPage(self, source):
        source.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_right)
        source.addFunction(EVENT_NEXT_PAGE, self.getFocus, self.getFocusObj)

    def __scopeSendEventSwitchFocus(self, source):
        source.addTask("TaskMovie2ButtonClick", Movie2Button=self.button_menu)
        source.addFunction(self.__setFocus, True)
        source.addFunction(EVENT_SWITCH_FOCUS, self.getFocus, self.getFocusObj)

    def __scopeReceiveEventsFeedback(self, source):
        with source.addRaceTask(3) as (race_1, race_2, race_3):
            race_1.addEvent(EVENT_PREV_PAGE_FB, self.__eventFeedback)
            race_2.addEvent(EVENT_NEXT_PAGE_FB, self.__eventFeedback)
            race_3.addEvent(EVENT_SWITCH_FOCUS_FB, self.__eventFeedback)
        source.addFunction(self.updatePageCounter)

    def __scopeLeaveScene(self, source):
        PreviousSceneName = self.demon_object.getParam('PreviousSceneName') or "Menu"
        source.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_back)
        source.addFunction(TransitionManager.changeScene, PreviousSceneName)
        source.addFunction(self.demon_object.setParam, 'PreviousSceneName', None)

    def enableTC(self):
        self.tc_leave_scene = TaskManager.createTaskChain(Repeat=True, Name="GuideNavigationLeaveScene")

        self.tc_receive_events_feedback = TaskManager.createTaskChain(Repeat=True, Name="GuideNavigationEventsFeedback")

        self.tc_send_event_prev_page = TaskManager.createTaskChain(Repeat=True, Name="GuideNavigationPageLeft")
        self.tc_send_event_next_page = TaskManager.createTaskChain(Repeat=True, Name="GuideNavigationPageRight")
        self.tc_send_event_switch_focus = TaskManager.createTaskChain(Repeat=True, Name="GuideNavigationSwitchFocus")

        with self.tc_leave_scene as tc:
            tc.addScope(self.__scopeLeaveScene)

        with self.tc_receive_events_feedback as tc:
            tc.addScope(self.__scopeReceiveEventsFeedback)

        with self.tc_send_event_prev_page as tc:
            tc.addScope(self.__scopeSendEventPrevPage)

        with self.tc_send_event_next_page as tc:
            tc.addScope(self.__scopeSendEventNextPage)

        with self.tc_send_event_switch_focus as tc:
            tc.addScope(self.__scopeSendEventSwitchFocus)

    def disableTC(self):
        self.tc_leave_scene.cancel()
        self.tc_receive_events_feedback.cancel()
        self.tc_send_event_prev_page.cancel()
        self.tc_send_event_next_page.cancel()
        self.tc_send_event_switch_focus.cancel()


class ChapterPagePicture(object):
    def __init__(self, page_movie, pic_movie, pic_slot):
        self.pic_movie = pic_movie
        self.pic_slot = pic_slot

        self.zoomed = False

        self.page_movie_en = page_movie.getEntityNode()
        self.pic_movie_en = pic_movie.getEntityNode()

    def setZoomed(self, zoomed):
        self.zoomed = zoomed

    def getZoomed(self):
        return self.zoomed

    def toTopLayer(self):
        self.page_movie_en.addChild(self.pic_movie_en)
        self.pic_movie_en.setLocalPosition(self.pic_slot.getWorldPosition())

    def layerRestore(self):
        self.pic_slot.addChild(self.pic_movie_en)
        self.pic_movie_en.setLocalPosition(self.pic_slot.getLocalPosition())

    def scopeClick(self, source):
        source.addTask("TaskMovie2SocketClick", Movie2=self.pic_movie, SocketName='socket')

    def scopeZoomIn(self, source):
        with source.addParallelTask(3) as (parallel_1, parallel_2, parallel_3):
            parallel_1.addTask("TaskNodeMoveTo", Node=self.pic_movie_en, To=ZOOM_IN_MOVE_TO, Time=ZOOM_IN_OUT_TIME)
            parallel_2.addTask("TaskNodeScaleTo", Node=self.pic_movie_en, To=ZOOM_IN_SCALE_TO, Time=ZOOM_IN_OUT_TIME)
            parallel_3.addPlay(self.pic_movie, Wait=False)

    def scopeZoomOut(self, source):
        with source.addParallelTask(3) as (parallel_1, parallel_2, parallel_3):
            to = self.pic_slot.getWorldPosition()

            parallel_1.addTask("TaskNodeMoveTo", Node=self.pic_movie_en, To=to, Time=ZOOM_IN_OUT_TIME)
            parallel_2.addTask("TaskNodeScaleTo", Node=self.pic_movie_en, To=ZOOM_OUT_SCALE_TO, Time=ZOOM_IN_OUT_TIME)
            parallel_3.addPlay(self.pic_movie, Wait=False)


class ChapterPage(object):
    ENTITY_OBJECT = None
    ERROR_COUNT = 0

    def __init__(self, chapter_page_param):
        self.chapter_page_param = chapter_page_param

        self.focus = False
        self.movie = None

        self.chapter_page_pics = list()
        self.__tc_pics_zoom = None

    def __createPageMovie(self):
        page_movie_proto_name = self.chapter_page_param.prototype_movie_name
        proto_name_unique = '{}_{}'.format(page_movie_proto_name, self.chapter_page_param.unique_index)

        self.movie = self.ENTITY_OBJECT.tryGenerateObjectUnique(proto_name_unique, page_movie_proto_name, Enable=True)
        if self.movie is None:
            ChapterPage.ERROR_COUNT += 1
            Trace.msg_err('[ERROR_{}]: CANT CREATE MOVIE CHAPTER PAGE {} FROM PROTOTYPE {}'.format(
                ChapterPage.ERROR_COUNT, proto_name_unique, page_movie_proto_name))
            return False

        self.ENTITY_OBJECT.entity.addChild(self.movie.getEntityNode())

        return True

    def __removePageMovie(self):
        movie = self.movie
        if movie is not None:
            movie.removeFromParent()
            movie.onFinalize()
            movie.onDestroy()
            self.movie = None

    def __setupTextIDs(self):
        text_env = str(self.chapter_page_param.unique_index)
        self.movie.setTextAliasEnvironment(text_env)

        for list_index, text_id in enumerate(self.chapter_page_param.page_text_ids):
            if text_id is None or text_id == -1:
                continue

            text_alias = PAGE_PROTOTYPE_MOVIE_TEXT_ALIAS_PREFIX + str(list_index)

            if not self.movie.entity.hasMovieText(text_alias):
                ChapterPage.ERROR_COUNT += 1
                Trace.msg_err('[ERROR_{}]: MOVIE {} CANT FIND TEXT ALIAS {} FOR TEXT {}'.format(
                    ChapterPage.ERROR_COUNT, self.movie.getName(), text_alias, text_id))
                continue

            if not Mengine.existText(text_id):
                ChapterPage.ERROR_COUNT += 1
                Trace.msg_err('[ERROR_{}]: CANT FIND TEXT ID {} IN Texts.xml FOR MOVIE {}'.format(
                    ChapterPage.ERROR_COUNT, text_id, self.movie.getName()))

                if Mengine.existText(ID_TEXT_PAGE_PROTOTYPE_404):
                    Mengine.setTextAlias(text_env, text_alias, ID_TEXT_PAGE_PROTOTYPE_404)

                elif Mengine.existText(ID_EMPTY_TEXT):
                    Mengine.setTextAlias(text_env, text_alias, ID_EMPTY_TEXT)

                continue

            Mengine.setTextAlias(text_env, text_alias, text_id)

    def __createPics(self):
        page_unique_id = self.chapter_page_param.unique_index
        generate_unique_movie = self.ENTITY_OBJECT.tryGenerateObjectUnique

        for list_index, pic_movie_proto_name in enumerate(self.chapter_page_param.page_pic_slots):
            if pic_movie_proto_name is None or pic_movie_proto_name == -1:
                continue

            proto_name_unique = '{}_{}_{}'.format(pic_movie_proto_name, page_unique_id, list_index)

            movie_pic = generate_unique_movie(proto_name_unique, pic_movie_proto_name, Enable=True)
            if movie_pic is None:
                ChapterPage.ERROR_COUNT += 1
                Trace.msg_err('[ERROR_{}]: CANT CREATE MOVIE PIC {} FROM PROTOTYPE {}'.format(
                    ChapterPage.ERROR_COUNT, proto_name_unique, pic_movie_proto_name))
                continue

            slot = self.movie.getMovieSlot(PAGE_PROTOTYPE_MOVIE_PIC_SLOT_PREFIX + str(list_index))
            if slot is None:
                ChapterPage.ERROR_COUNT += 1
                slot_name = PAGE_PROTOTYPE_MOVIE_PIC_SLOT_PREFIX + str(list_index)
                Trace.msg_err('[ERROR_{}]: NOT FOUND MOVIE SLOT {} in {} TO ATTACH MOVIE PIC {}'.format(
                    ChapterPage.ERROR_COUNT, slot_name, self.movie.getName(), proto_name_unique))
                continue

            slot.addChild(movie_pic.getEntityNode())
            chapter_page_pic = ChapterPagePicture(self.movie, movie_pic, slot)
            self.chapter_page_pics.append(chapter_page_pic)

        return len(self.chapter_page_pics) > 0

    def __removePics(self):
        for page_pic in self.chapter_page_pics:
            pic_movie = page_pic.pic_movie
            pic_movie.removeFromParent()
            pic_movie.onFinalize()
            pic_movie.onDestroy()

        self.chapter_page_pics = []

    @staticmethod
    def __scopeResolvePicsClick(source, holder_pic_cur, holder_pic_prev):
        cur_pic = holder_pic_cur.get()
        prev_pic = holder_pic_prev.get()

        with source.addIfTask(cur_pic.getZoomed) as (true, false):
            true.addScope(cur_pic.scopeZoomOut)
            true.addFunction(cur_pic.setZoomed, False)
            true.addFunction(cur_pic.layerRestore)

            with false.addParallelTask(2) as (parallel_0, parallel_1):
                if prev_pic is not None and prev_pic.zoomed:
                    parallel_0.addScope(prev_pic.scopeZoomOut)
                    parallel_0.addFunction(prev_pic.setZoomed, False)
                    parallel_0.addFunction(prev_pic.layerRestore)

                parallel_1.addFunction(cur_pic.toTopLayer)
                parallel_1.addScope(cur_pic.scopeZoomIn)
                parallel_1.addFunction(cur_pic.setZoomed, True)
                parallel_1.addFunction(holder_pic_prev.set, cur_pic)

    def enableTC(self):
        time = Mengine.getTimeMs()

        if self.__createPageMovie() is False:
            return False

        self.__setupTextIDs()

        if self.__createPics() is False:
            return False

        self.__tc_pics_zoom = TaskManager.createTaskChain(Repeat=True)

        pic_holder_prev = Holder()
        pic_holder_cur = Holder()

        with self.__tc_pics_zoom as tc:
            for pic, race in tc.addRaceTaskList(self.chapter_page_pics):
                race.addScope(pic.scopeClick)
                race.addFunction(pic_holder_cur.set, pic)

            tc.addScope(self.__scopeResolvePicsClick, pic_holder_cur, pic_holder_prev)

        return True

    def disableTC(self):
        if self.__tc_pics_zoom is not None:
            self.__tc_pics_zoom.cancel()

        self.__removePics()
        self.__removePageMovie()

    def setFocus(self, focus):
        if focus:
            if self.enableTC() is False:
                return
        else:
            self.disableTC()

        if self.movie is not None:
            self.movie.setEnable(focus)
        self.focus = focus


class Chapter(object):
    def __init__(self, chapter_id, button_chapter):
        self.chapter_id = chapter_id
        self.button_chapter = button_chapter
        self.chapter_pages = list()

        self.tc_receive_event_prev_page = None
        self.tc_receive_event_next_page = None
        self.tc_receive_event_switch_focus = None

        self.tc_send_event_switch_focus = None

        self.button_chapter.setEnable(False)

        self.chapter_page_in_focus = None
        self.chapter_page_in_focus_index = 0

    def addChapterPage(self, chapter_page):
        self.chapter_pages.append(chapter_page)

    def getFocusPageNumber(self):
        return self.chapter_page_in_focus_index + 1

    def getPagesNumber(self):
        return len(self.chapter_pages)

    def __filterEventPagination(self, focus_getter, focus_obj_getter):
        if not focus_getter() and focus_obj_getter() is self:
            return True
        return False

    def __setPrevPage(self):
        if self.chapter_page_in_focus_index is 0:
            return

        self.chapter_page_in_focus.setFocus(False)
        self.chapter_page_in_focus_index -= 1
        self.chapter_page_in_focus = self.chapter_pages[self.chapter_page_in_focus_index]
        self.chapter_page_in_focus.setFocus(True)

    def __scopePrevPage(self, source):
        source.addEvent(EVENT_PREV_PAGE, self.__filterEventPagination)
        source.addFunction(self.__setPrevPage)
        source.addFunction(EVENT_PREV_PAGE_FB, False, self)

    def __setNextPage(self):
        if self.chapter_page_in_focus_index + 1 is len(self.chapter_pages):
            return

        self.chapter_page_in_focus.setFocus(False)
        self.chapter_page_in_focus_index += 1
        self.chapter_page_in_focus = self.chapter_pages[self.chapter_page_in_focus_index]
        self.chapter_page_in_focus.setFocus(True)

    def __scopeNextPage(self, source):
        source.addEvent(EVENT_NEXT_PAGE, self.__filterEventPagination)
        source.addFunction(self.__setNextPage)
        source.addFunction(EVENT_NEXT_PAGE_FB, False, self)

    @staticmethod
    def __filterEventFocus(focus_getter, _):
        return focus_getter()

    def __switchFocus(self):
        if self.chapter_page_in_focus is None:
            self.chapter_page_in_focus = self.chapter_pages[self.chapter_page_in_focus_index]
        self.chapter_page_in_focus.setFocus(False)

    def __scopeSwitchFocus(self, source):
        source.addEvent(EVENT_SWITCH_FOCUS, self.__filterEventFocus)
        source.addFunction(self.__switchFocus)

    def __chapterSelect(self):
        self.chapter_page_in_focus = self.chapter_pages[self.chapter_page_in_focus_index]
        self.chapter_page_in_focus.setFocus(True)

    def __scopeChapterSelect(self, source):
        source.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_chapter)
        source.addFunction(self.__chapterSelect)
        source.addFunction(EVENT_SWITCH_FOCUS, lambda: False, lambda: self)
        source.addFunction(EVENT_SWITCH_FOCUS_FB, False, self)

    def enableTC(self):
        button_name = self.button_chapter.getName()

        self.tc_send_event_switch_focus = TaskManager.createTaskChain(Repeat=True, Name="GuideChapterChapterSelect{}".format(button_name))

        self.tc_receive_event_prev_page = TaskManager.createTaskChain(Repeat=True, Name='GuideChapterPrevPage{}'.format(button_name))

        self.tc_receive_event_next_page = TaskManager.createTaskChain(Repeat=True, Name='GuideChapterNextPage{}'.format(button_name))

        self.tc_receive_event_switch_focus = TaskManager.createTaskChain(Repeat=True, Name='GuideChapterSwitchFocus{}'.format(button_name))

        with self.tc_send_event_switch_focus as tc:
            tc.addScope(self.__scopeChapterSelect)

        with self.tc_receive_event_prev_page as tc:
            tc.addScope(self.__scopePrevPage)

        with self.tc_receive_event_next_page as tc:
            tc.addScope(self.__scopeNextPage)

        with self.tc_receive_event_switch_focus as tc:
            tc.addScope(self.__scopeSwitchFocus)

    def disableTC(self):
        self.tc_send_event_switch_focus.cancel()
        self.tc_receive_event_prev_page.cancel()
        self.tc_receive_event_next_page.cancel()
        self.tc_receive_event_switch_focus.cancel()


class MenuPage(object):
    def __init__(self, menu_page_id):
        self.menu_page_id = menu_page_id

        self.chapters = list()

        self.focus = False

    def setFocus(self, focus):
        for chapter in self.chapters:
            chapter.button_chapter.setEnable(focus)

        self.focus = focus

    def addChapter(self, chapter):
        self.chapters.append(chapter)


class Menu(object):
    def __init__(self):
        self.menu_pages = list()

        self.tc_receive_event_prev_page = None
        self.tc_receive_event_next_page = None
        self.tc_receive_event_switch_focus = None

        self.menu_page_in_focus_index = 0
        self.menu_page_in_focus = None

    def addMenuPage(self, menu_page):
        self.menu_pages.append(menu_page)

    def getFocusPageNumber(self):
        return self.menu_page_in_focus_index + 1

    def getPagesNumber(self):
        return len(self.menu_pages)

    @staticmethod
    def __filterEventPagination(focus_getter, _):
        return focus_getter()

    def __setPrevPage(self):
        if self.menu_page_in_focus_index is 0:
            return

        self.menu_page_in_focus.setFocus(False)
        self.menu_page_in_focus_index -= 1
        self.menu_page_in_focus = self.menu_pages[self.menu_page_in_focus_index]
        self.menu_page_in_focus.setFocus(True)

    def __scopePrevPage(self, source):
        source.addEvent(EVENT_PREV_PAGE, self.__filterEventPagination)
        source.addFunction(self.__setPrevPage)
        source.addFunction(EVENT_PREV_PAGE_FB, True, self)

    def __setNextPage(self):
        if self.menu_page_in_focus_index + 1 is len(self.menu_pages):
            return

        self.menu_page_in_focus.setFocus(False)
        self.menu_page_in_focus_index += 1
        self.menu_page_in_focus = self.menu_pages[self.menu_page_in_focus_index]
        self.menu_page_in_focus.setFocus(True)

    def __scopeNextPage(self, source):
        source.addEvent(EVENT_NEXT_PAGE, self.__filterEventPagination)
        source.addFunction(self.__setNextPage)
        source.addFunction(EVENT_NEXT_PAGE_FB, True, self)

    def __switchFocus(self, focus):
        self.menu_page_in_focus.setFocus(focus)

    def __filterEventFocus(self, focus_getter, _):
        self.__switchFocus(focus_getter())
        return focus_getter()

    def __scopeSwitchFocus(self, source):
        source.addEvent(EVENT_SWITCH_FOCUS, self.__filterEventFocus)
        source.addFunction(EVENT_SWITCH_FOCUS_FB, True, self)

    def enableTC(self):
        self.tc_receive_event_prev_page = TaskManager.createTaskChain(Repeat=True, Name='GuideMenuPrevPage')
        self.tc_receive_event_next_page = TaskManager.createTaskChain(Repeat=True, Name='GuideMenuNextPage')
        self.tc_receive_event_switch_focus = TaskManager.createTaskChain(Repeat=True, Name='GuideMenuMenu')

        with self.tc_receive_event_prev_page as tc:
            tc.addScope(self.__scopePrevPage)

        with self.tc_receive_event_next_page as tc:
            tc.addScope(self.__scopeNextPage)

        with self.tc_receive_event_switch_focus as tc:
            tc.addScope(self.__scopeSwitchFocus)

    def disableTC(self):
        self.tc_receive_event_prev_page.cancel()
        self.tc_receive_event_next_page.cancel()
        self.tc_receive_event_switch_focus.cancel()


class Guide(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        Type.addActionActivate("PreviousSceneName")

    def __init__(self):
        super(Guide, self).__init__()
        self.navigation = None

        self.menu = None
        self.menu_pages = list()

        self.chapters = list()
        self.chapter_pages = list()

    def _onPreparation(self):
        button_back = self.object.getObject(NAV_BUTTON_BACK_NAME)
        button_menu = self.object.getObject(NAV_BUTTON_MENU_NAME)
        button_left = self.object.getObject(NAV_BUTTON_LEFT_NAME)
        button_right = self.object.getObject(NAV_BUTTON_RIGHT_NAME)
        page_counter = self.object.getObject(NAV_BUTTON_COUNTER_MOVIE_NAME)

        self.navigation = Navigation(self.object, button_back, button_menu, button_left, button_right, page_counter)

        self.menu = Menu()

        ChapterPage.ENTITY_OBJECT = self.object

        for menu_page_param in GUIDE_PARAM.menu_pages:
            menu_page = MenuPage(menu_page_param.index)
            self.menu.addMenuPage(menu_page)
            self.menu_pages.append(menu_page)

            for chapter_param in menu_page_param.chapters:
                chapter_button = self.object.getObject(chapter_param.button_name)
                chapter = Chapter(chapter_param.index, chapter_button)
                menu_page.addChapter(chapter)
                self.chapters.append(chapter)

                for chapter_page_param in chapter_param.pages:
                    chapter_page = ChapterPage(chapter_page_param)
                    chapter.addChapterPage(chapter_page)
                    self.chapter_pages.append(chapter_page)

    def _onActivate(self):
        nav_focus, menu_page_index, chapter_index, chapter_page_index = SystemGuide.getDataCache()

        menu = self.menu
        menu_page = menu.menu_pages[menu_page_index]
        menu.menu_page_in_focus_index = menu_page_index
        menu.menu_page_in_focus = menu_page
        menu_page.setFocus(nav_focus)

        chapter = self.menu.menu_pages[menu_page_index].chapters[chapter_index]
        chapter_page = chapter.chapter_pages[chapter_page_index]
        chapter.chapter_page_in_focus_index = chapter_page_index
        chapter.chapter_page_in_focus = chapter_page
        chapter_page.setFocus(not nav_focus)

        self.navigation.chapter_obj = chapter
        self.navigation.menu_obj = self.menu
        self.navigation.focus = nav_focus
        self.navigation.updatePageCounter()
        self.navigation.enableTC()

        self.menu.enableTC()

        for chapter in self.chapters:
            chapter.enableTC()

        button_menu = self.navigation.button_menu
        button_menu.setBlock(nav_focus)

    def _onDeactivate(self):
        SystemGuide.cacheData(navigation_focus_param=self.navigation.focus,
                              menu_page_obj_index=self.navigation.menu_obj.menu_page_in_focus_index,
                              chapter_obj_index=0 if self.navigation.chapter_obj is None else self.navigation.chapter_obj.chapter_id,
                              chapter_page_obj_index=0 if self.navigation.chapter_obj is None else self.navigation.chapter_obj.chapter_page_in_focus_index)

        self.navigation.disableTC()

        self.menu.disableTC()

        for chapter in self.chapters:
            chapter.disableTC()

        for chapter_page in self.chapter_pages:
            chapter_page.disableTC()
