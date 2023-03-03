from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from HOPA.TransitionManager import TransitionManager


class ChapterSelectionManager(Manager):
    s_chapter_current = None
    s_chapter_selection_params = {}

    class ChapterSelectionParam(object):
        def __init__(self, chapter_name, chapter_plate_name, chapter_plate_block, is_main_chapter, text_id_open_chapter,
                     text_id_close_chapter, start_scene, map_demon_name, map_scene_name, map_group_name,
                     start_cut_scene, is_open, open_chapter_movie_name, on_chapter_reset_saved_systems,
                     start_paragraph):
            self.chapter_name = chapter_name
            self.start_scene = start_scene
            self.start_cut_scene = start_cut_scene
            self.map_demon_name = map_demon_name
            self.map_scene_name = map_scene_name
            self.map_group_name = map_group_name
            self.chapter_plate_name = chapter_plate_name
            self.chapter_plate_block_name = chapter_plate_block
            self.is_main_chapter = is_main_chapter  # Main chapter always available
            self.is_open = is_open
            self.open_chapter_movie_name = open_chapter_movie_name
            self.text_id_open_chapter = text_id_open_chapter
            self.text_id_close_chapter = text_id_close_chapter
            self.on_chapter_reset_saved_systems = on_chapter_reset_saved_systems
            self.on_chapter_reset_saved_paragraphs = []
            self.start_paragraph = start_paragraph

        def isMain(self):
            return self.is_main_chapter

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        if param == 'ChapterSelection':
            for record in records:
                '''
                    ChapterSelection.xlsx:
                    ChapterName	isMain	ChapterPlate	StartScene	StartCutScene
                    DemonMapName    MapSceneName    MapGroupName
                    OpenChapterTextID	CloseChapterTextID
                    [onChapterResetSavedSystems]
                '''
                chapter_name = record.get("ChapterName")
                chapter_plate_name = record.get("ChapterPlate")
                chapter_plate_block = record.get("ChapterPlateBlock")
                text_id_open_chapter = record.get("OpenChapterTextID")
                text_id_close_chapter = record.get("CloseChapterTextID")
                start_scene = record.get("StartScene")
                start_cut_scene = record.get("StartCutScene")
                map_demon_name = record.get("DemonMapName")
                map_group_name = record.get("MapGroupName")
                map_scene_name = record.get("MapSceneName")
                open_chapter_movie_name = record.get("OpenChapterMovieName")
                is_main_chapter = record.get("isMain", 0)
                is_main_chapter = bool(int(is_main_chapter))
                is_open = record.get("isOpen", 0)
                is_open = bool(int(is_open))
                on_chapter_reset_saved_systems = record.get("onChapterResetSavedSystems", [])
                start_paragraph = record.get("StartParagraph")

                param = ChapterSelectionManager.ChapterSelectionParam(chapter_name, chapter_plate_name,
                                                                      chapter_plate_block, is_main_chapter,
                                                                      text_id_open_chapter, text_id_close_chapter,
                                                                      start_scene, map_demon_name, map_scene_name,
                                                                      map_group_name, start_cut_scene, is_open,
                                                                      open_chapter_movie_name,
                                                                      on_chapter_reset_saved_systems, start_paragraph)

                ChapterSelectionManager.s_chapter_selection_params[chapter_name] = param

        elif param == 'ChapterSelectionResetChapterParagraphs':
            for record in records:
                '''
                    ChapterSelectionResetChapterParagraphs.xlsx:
                    ChapterName [onChapterResetSavedParagraphs]
                '''
                chapter_name = record.get("ChapterName")
                on_chapter_reset_saved_paragraphs = record.get("onChapterResetSavedParagraphs", [])
                if chapter_name not in ChapterSelectionManager.s_chapter_selection_params:
                    continue
                ChapterSelectionManager.s_chapter_selection_params[
                    chapter_name].on_chapter_reset_saved_paragraphs = on_chapter_reset_saved_paragraphs

        return True

    @staticmethod
    def setCurrentChapter(chapter_name):
        ChapterSelectionManager.s_chapter_current = chapter_name

    @staticmethod
    def getCurrentChapter():
        return ChapterSelectionManager.s_chapter_current

    @staticmethod
    def getChapterSelectionParams():
        return ChapterSelectionManager.s_chapter_selection_params

    @staticmethod
    def getFirstValidParam():
        for chapter in ChapterSelectionManager.s_chapter_selection_params.itervalues():
            if chapter:
                return chapter

    @staticmethod
    def getParamByChaptersAnyScene(scene_name):
        """
        if scene is in first chapter range -> return first chapter param
        if scene is in bonus chapter range -> return second chapter param
        """
        spiral_scenes = TransitionManager.findSpiralScenes(scene_name)
        if not spiral_scenes:
            return

        for param in ChapterSelectionManager.s_chapter_selection_params.itervalues():
            if param.start_scene in spiral_scenes:
                return param

    @staticmethod
    def getChapterSelectionParam(chapter_name):
        return ChapterSelectionManager.s_chapter_selection_params.get(chapter_name)

    @staticmethod
    def getCurrentMapSceneName():
        current_chapter_name = ChapterSelectionManager.getCurrentChapter()
        current_chapter_param = ChapterSelectionManager.getChapterSelectionParam(current_chapter_name)

        if current_chapter_param is not None:
            return current_chapter_param.map_scene_name

    @staticmethod
    def getCurrentMapGroupName():
        current_chapter_name = ChapterSelectionManager.getCurrentChapter()
        current_chapter_param = ChapterSelectionManager.getChapterSelectionParam(current_chapter_name)
        if current_chapter_param is None:
            return None
        return current_chapter_param.map_group_name
