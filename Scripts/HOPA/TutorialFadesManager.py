from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager

class TutorialFadesManager(Manager):
    s_data = {}
    s_is_active_tutorial = True
    s_tutorial_complete = False

    class Param(object):
        def __init__(self, fade_show_name, fade_hide_name, fade_id, group_name):
            self.fadeID = fade_id
            self.showName = fade_show_name
            self.hideName = fade_hide_name
            self.groupName = group_name

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            fade_id = record.get("FadeID")
            fade_show_name = record.get("FadeShowName")
            fade_hide_name = record.get("FadeHideName")
            group_name = record.get("GroupName")

            new_param = TutorialFadesManager.Param(fade_show_name, fade_hide_name, fade_id, group_name)
            TutorialFadesManager.s_data[fade_id] = new_param

        return True

    @staticmethod
    def getParam():
        return TutorialFadesManager.s_data

    @staticmethod
    def setActiveTutorialState(value):
        TutorialFadesManager.s_is_active_tutorial = value

    @staticmethod
    def isActiveTutorial():
        return TutorialFadesManager.s_is_active_tutorial

    @staticmethod
    def completeTutorial():
        TutorialFadesManager.s_tutorial_complete = True

    @staticmethod
    def isTutorialComplete():
        return TutorialFadesManager.s_tutorial_complete