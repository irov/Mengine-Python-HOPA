from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager
from Foundation.Utils import isCollectorEdition

class MenuPageParam(object):
    def __init__(self, index):
        self.index = index

        self.chapters = list()

class ChapterParam(object):
    def __init__(self, index, button_name):
        self.index = index
        self.button_name = button_name

        self.pages = list()

class PageParam(object):
    def __init__(self, unique_index, index, prototype_movie_name):
        self.unique_index = unique_index
        self.index = index
        self.prototype_movie_name = prototype_movie_name

        self.page_pic_slots = list()
        self.page_text_ids = list()

class GuideParam(object):
    def __init__(self, pic_zoom_pos, pic_zoom_scale, pic_zoom_time, menu_pages):
        self.pic_zoom_pos = pic_zoom_pos
        self.pic_zoom_scale = pic_zoom_scale
        self.pic_zoom_time = pic_zoom_time
        self.menu_pages = menu_pages

class GuideManager(Manager):
    s_guide_param = None

    @staticmethod
    def loadParams(module, param):
        if isCollectorEdition() is False:
            return True

        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            '''
            PicZoomPosX	PicZoomPosY	PicZoomScaleX	PicZoomScaleY	PicZoomTime	GuidePages	GuidePagesPics	GuidePagesTexts
            '''
            pic_zoom_pos = (record.get('PicZoomPosX'), record.get('PicZoomPosY'))
            pic_zoom_scale = (record.get('PicZoomScaleX'), record.get('PicZoomScaleY'))
            pic_zoom_time = record.get('PicZoomTime')
            guide_pages = record.get('GuidePages')
            guide_pages_pics = record.get('GuidePagesPics')
            guide_pages_texts = record.get('GuidePagesTexts')

            result = GuideManager.addParam(module, guide_pages, guide_pages_pics, guide_pages_texts, pic_zoom_pos, pic_zoom_scale, pic_zoom_time)

            if result is False:
                error_msg = "GuideManager invalid addParam"
                Trace.log("Manager", 0, error_msg)
                return False
        return True

    @staticmethod
    def addParam(module, guide_pages, guide_pages_pics, guide_pages_texts, pic_zoom_pos, pic_zoom_scale, pic_zoom_time):
        records = DatabaseManager.getDatabaseRecords(module, guide_pages)
        if records is None:
            Trace.log("Manager", 0, "GuideManager cant find GuidePages database")
            return False

        menu_pages = list()

        temp_pages_param = dict()

        for record in records:
            '''
            MenuPageIndex	ChapterButtonIndex	ChapterPageIndex	ChapterButton	ChapterPagePrototype PageUniqueIndex
            '''
            menu_page_id = record.get('MenuPageIndex')
            chapter_id = record.get('ChapterButtonIndex')
            page_id = record.get('ChapterPageIndex')
            chapter_button = record.get('ChapterButton')
            chapter_page_prototype = record.get('ChapterPagePrototype')
            page_unique_index = record.get('PageUniqueIndex')

            if menu_page_id == len(menu_pages):
                menu_page = MenuPageParam(menu_page_id)
                menu_pages.append(menu_page)
            menu_page = menu_pages[menu_page_id]

            if chapter_id == len(menu_page.chapters):
                chapter = ChapterParam(chapter_id, chapter_button)
                menu_page.chapters.append(chapter)
            chapter = menu_page.chapters[chapter_id]

            if page_id == len(chapter.pages):
                page = PageParam(page_unique_index, page_id, chapter_page_prototype)
                chapter.pages.append(page)

                temp_pages_param[page_unique_index] = page

        records = DatabaseManager.getDatabaseRecords(module, guide_pages_pics)
        if records is None:
            Trace.log("Manager", 0, "GuideManager cant find GuidePagesPics database")
            return False

        for record in records:
            '''
            PageUniqueIndex	[PicSlots]
            '''
            page_unique_index = record.get('PageUniqueIndex')
            page_pic_slots = record.get('PicSlots', [])

            temp_pages_param[page_unique_index].page_pic_slots = page_pic_slots

        records = DatabaseManager.getDatabaseRecords(module, guide_pages_texts)
        if records is None:
            Trace.log("Manager", 0, "GuideManager cant find GuidePagesTexts database")
            return False

        for record in records:
            '''
            PageUniqueIndex	[TextIDs]
            '''
            page_unique_index = record.get('PageUniqueIndex')
            page_text_ids = record.get('TextIDs', [])

            temp_pages_param[page_unique_index].page_text_ids = page_text_ids

        GuideManager.s_guide_param = GuideParam(pic_zoom_pos, pic_zoom_scale, pic_zoom_time, menu_pages)

    @staticmethod
    def getGuideParams():
        return GuideManager.s_guide_param