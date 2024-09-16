from Foundation.ArrowManager import ArrowManager
from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Notificator import Notificator
from Foundation.SceneManager import SceneManager
from Foundation.SystemManager import SystemManager
from Foundation.TaskManager import TaskManager
from HOPA.ChapterSelectionManager import ChapterSelectionManager


TEXT_ALIAS_TEXT_CURSOR = '$AliasTextOnCursorChapterSelection'
TEXT_ID_TEXT_CURSOR_EMPTY = 'ID_CHAPTER_SELECTION_EMPTY'
ID_POPUP_RESTART_CHAPTER = 'ID_POPUP_RESTART_CHAPTER'


class ChapterPlate(object):
    def __init__(self, button_plate, button_plate_block, open_chapter_animation, param):
        self.id = param.chapter_name
        self.button_plate = button_plate
        self.button_plate_block = button_plate_block
        self.open_chapter_animation = open_chapter_animation
        self.chapter_data = param

        self.setPlateState()

    def setPlateState(self):
        if self.chapter_data.param.isMain():
            return

        if self.chapter_data.isOpen() and not self.chapter_data.isBlocked():
            self.button_plate.setEnable(True)
            if self.button_plate_block is not None:
                self.button_plate_block.setEnable(False)
        else:
            self.button_plate.setEnable(False)
            self.button_plate_block.setEnable(True)

    def scopeClick(self, source):
        if self.button_plate.getEnable() is False:
            source.addBlock()
            return
        source.addTask('TaskMovie2ButtonClick', Movie2Button=self.button_plate)

    def setTextCursor(self, is_leave):
        if is_leave is True:
            Mengine.setTextAlias('', TEXT_ALIAS_TEXT_CURSOR, TEXT_ID_TEXT_CURSOR_EMPTY)
            return

        text_id = self.chapter_data.param.text_id_open_chapter if self.chapter_data.isOpen() else self.chapter_data.param.text_id_close_chapter
        Mengine.setTextAlias('', TEXT_ALIAS_TEXT_CURSOR, text_id)

    def scopeEnter(self, source):
        current_plate_obj = self.button_plate if self.chapter_data.isOpen() else self.button_plate_block

        source.addListener(Notificator.onMovie2ButtonMouseEnter, Filter=lambda obj: obj is current_plate_obj)
        source.addFunction(self.setTextCursor, False)

    def scopeLeave(self, source):
        current_plate_obj = self.button_plate if self.chapter_data.isOpen() else self.button_plate_block

        source.addListener(Notificator.onMovie2ButtonMouseLeave, Filter=lambda obj: obj is current_plate_obj)
        source.addFunction(self.setTextCursor, True)


class ChapterSelection(BaseEntity):
    """
        here the chapter is understood as main game and dlc (example main and bonus)
    """

    def __init__(self):
        super(ChapterSelection, self).__init__()

        self.chapter_plates = []
        self.tc = None
        self.bg = None
        self.movie_text_on_cursor = None

    def _onPreparation(self):
        self.chapter_plates = []  # mem leak fix
        self.bg = self.object.getObject('Movie2_BG')
        self.movie_text_on_cursor = self.object.getObject('Movie2_CursorText')

        self._setupCursorText()

        system_chapter_selection = SystemManager.getSystem('SystemChapterSelection')

        self.chapter_selection_params = system_chapter_selection.getChapterSelections()
        for chapter in self.chapter_selection_params.values():
            button_plate = self.object.getObject(chapter.param.chapter_plate_name)

            button_plate_block = None
            if chapter.param.chapter_plate_block_name is not None:
                button_plate_block = self.object.getObject(chapter.param.chapter_plate_block_name)

            open_chapter_animation = None
            if self.object.hasObject(chapter.param.open_chapter_movie_name):
                open_chapter_animation = self.object.getObject(chapter.param.open_chapter_movie_name)

            chapter_plate = ChapterPlate(button_plate, button_plate_block, open_chapter_animation, chapter)
            self.chapter_plates.append(chapter_plate)

        self._setupTitles()

    def _setupCursorText(self):
        node = self.movie_text_on_cursor.getEntityNode()

        if Mengine.hasTouchpad() is True:
            if self.bg.hasSlot("cursor_text_touchpad") is False:
                self.movie_text_on_cursor.setEnable(False)
            else:
                self.movie_text_on_cursor.setEnable(True)
                slot = self.bg.getMovieSlot("cursor_text_touchpad")
                slot.addChild(node)
        else:
            self.movie_text_on_cursor.setEnable(True)
            arrow = Mengine.getArrow()
            arrow_node = arrow.getNode()
            arrow_node.addChild(node)

        Mengine.setTextAlias('', TEXT_ALIAS_TEXT_CURSOR, TEXT_ID_TEXT_CURSOR_EMPTY)

    def _setupTitles(self):
        if self.object.hasObject("Movie2_ChapterNames") is False:
            return

        titles = self.object.getObject("Movie2_ChapterNames")

        if Mengine.hasTouchpad() is False:
            titles.setEnable(False)

    def _onActivate(self):
        self.__runTaskChain()

    def __runTaskChain(self):
        cur_scene_name = SceneManager.getCurrentSceneName()

        self.tc_click = TaskManager.createTaskChain(Repeat=True)
        self.tc_enter_leave = TaskManager.createTaskChain(Repeat=True)

        with self.tc_click as tc_click:
            with tc_click.addRaceTask(3) as (source_reset, source_select_chapter, source_cancel):
                with source_reset.addRaceTask(2) as (src_0, src_1):
                    src_0.addListener(Notificator.onChapterOpen)
                    src_1.addListener(Notificator.onChapterSelectionBlock)

                source_cancel.addTask('TaskMovie2SocketClick', Movie2=self.bg, SocketName='socket')
                source_cancel.addNotify(Notificator.onChapterSelectionChoseChapter, None)

                for (plate, source_plate) in source_select_chapter.addRaceTaskList(self.chapter_plates):
                    source_plate.addScope(self.scopeOpenAnimation, plate)
                    source_plate.addScope(plate.scopeClick)

                    with source_plate.addIfTask(lambda _plate: _plate.chapter_data.is_played, plate) as (true, false):
                        true.addFunction(plate.setTextCursor, True)
                        true.addTask("AliasMessageShow", TextID=ID_POPUP_RESTART_CHAPTER)

                        with true.addRaceTask(2) as (race_button_yes, race_button_no):
                            race_button_yes.addTask("AliasMessageYes")
                            race_button_yes.addTask("AliasMessageHide", SceneName=cur_scene_name)
                            race_button_yes.addNotify(Notificator.onChapterSelectionResetProfile, plate.id)
                            race_button_yes.addFunction(ChapterSelectionManager.setCurrentChapter, plate.id)
                            race_button_yes.addNotify(Notificator.onChapterSelectionChoseChapter, plate.id)

                            race_button_no.addTask("AliasMessageNo")
                            race_button_no.addTask("AliasMessageHide", SceneName=cur_scene_name)
                            race_button_no.addNotify(Notificator.onChapterSelectionChoseChapter, None)

                        false.addFunction(ChapterSelectionManager.setCurrentChapter, plate.id)
                        false.addNotify(Notificator.onChapterSelectionChoseChapter, plate.id)

        with self.tc_enter_leave as tc_enter_leave:
            for (plate, source_plate) in tc_enter_leave.addRaceTaskList(self.chapter_plates):
                source_plate.addScope(plate.scopeEnter)
                source_plate.addScope(plate.scopeLeave)

    def scopeOpenAnimation(self, source, chapter_plate):
        chapter_data = chapter_plate.chapter_data
        if not all([
            chapter_data.param.is_main_chapter is False,
            chapter_data.is_open is True,
            chapter_data.is_blocked is False,
            chapter_data.is_play_open_animation is False,
            chapter_plate.open_chapter_animation is not None
        ]):
            source.addDummy()
            return

        with GuardBlockInput(source) as guard_source:
            guard_source.addDisable(chapter_plate.button_plate)
            guard_source.addEnable(chapter_plate.open_chapter_animation)
            guard_source.addPlay(chapter_plate.open_chapter_animation, Loop=False, Wait=True)
            guard_source.addDisable(chapter_plate.open_chapter_animation)
            guard_source.addEnable(chapter_plate.button_plate)
            guard_source.addFunction(chapter_plate.setPlateState)  # for update state

        chapter_data.is_play_open_animation = True

    def _onDeactivate(self):
        self.__cleanUp()

    def __cleanUp(self):
        if self.tc_click is not None:
            self.tc_click.cancel()
        self.tc_click = None

        Mengine.setTextAlias('', TEXT_ALIAS_TEXT_CURSOR, TEXT_ID_TEXT_CURSOR_EMPTY)

        if self.tc_enter_leave is not None:
            self.tc_enter_leave.cancel()
        self.tc_enter_leave = None
