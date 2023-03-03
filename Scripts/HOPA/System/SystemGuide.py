from Foundation.PolicyManager import PolicyManager
from Foundation.System import System
from Foundation.Utils import isCollectorEdition


class SystemGuide(System):
    NAVIGATION_FOCUS_PARAM_CACHE = True
    MENU_PAGE_OBJ_INDEX_CACHE = 0
    CHAPTER_OBJ_INDEX_CACHE = 0
    CHAPTER_PAGE_OBJ_INDEX_CACHE = 0

    def _onRun(self):
        if isCollectorEdition() is False:
            return True

        SystemGuide.NAVIGATION_FOCUS_PARAM_CACHE = True
        SystemGuide.MENU_PAGE_OBJ_INDEX_CACHE = 0
        SystemGuide.CHAPTER_OBJ_INDEX_CACHE = 0
        SystemGuide.CHAPTER_PAGE_OBJ_INDEX_CACHE = 0

        self.runTaskChain()

        return True

    def runTaskChain(self):
        PolicyGuideOpen = PolicyManager.getPolicy("GuideOpen", "PolicyGuideOpenDefault")
        with self.createTaskChain(Name="GuideOpen", Repeat=True) as tc:
            tc.addTask(PolicyGuideOpen, GroupName="GuideOpen")

    @staticmethod
    def cacheData(navigation_focus_param=True, menu_page_obj_index=0, chapter_obj_index=0, chapter_page_obj_index=0):
        SystemGuide.NAVIGATION_FOCUS_PARAM_CACHE = navigation_focus_param
        SystemGuide.MENU_PAGE_OBJ_INDEX_CACHE = menu_page_obj_index
        SystemGuide.CHAPTER_OBJ_INDEX_CACHE = chapter_obj_index
        SystemGuide.CHAPTER_PAGE_OBJ_INDEX_CACHE = chapter_page_obj_index

    @staticmethod
    def getDataCache():
        return SystemGuide.NAVIGATION_FOCUS_PARAM_CACHE, \
            SystemGuide.MENU_PAGE_OBJ_INDEX_CACHE, \
            SystemGuide.CHAPTER_OBJ_INDEX_CACHE, \
            SystemGuide.CHAPTER_PAGE_OBJ_INDEX_CACHE

    @staticmethod
    def _onSave():
        return SystemGuide.NAVIGATION_FOCUS_PARAM_CACHE, \
            SystemGuide.MENU_PAGE_OBJ_INDEX_CACHE, \
            SystemGuide.CHAPTER_OBJ_INDEX_CACHE, \
            SystemGuide.CHAPTER_PAGE_OBJ_INDEX_CACHE

    @staticmethod
    def _onLoad(save_data):
        SystemGuide.NAVIGATION_FOCUS_PARAM_CACHE, \
            SystemGuide.MENU_PAGE_OBJ_INDEX_CACHE, \
            SystemGuide.CHAPTER_OBJ_INDEX_CACHE, \
            SystemGuide.CHAPTER_PAGE_OBJ_INDEX_CACHE = save_data
