from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class TutorialFadesManager(Manager):
    s_config = {}
    s_fades = {}
    s_is_active_tutorial = True
    s_tutorial_complete = False

    class Config(object):
        def __init__(self, records):
            self._params = {}

            for record in records:
                key = record.get("Key")
                value = record.get("Value")
                self._params[key] = value

        def get(self, key, default=None):
            return self._params.get(key, default)

    class Fades(object):
        def __init__(self, records):
            self._params = {}

            for record in records:
                fadeID = record.get("FadeID")
                fade_params = {
                    "showName": record.get("FadeShowName"),
                    "hideName": record.get("FadeHideName"),

                    "window_text": record.get("WindowTextID"),
                    "fade_movie": record.get("FadeMovie"),
                    "window_movie": record.get("WindowMovie")
                }

                self._params[fadeID] = fade_params

        def get(self, key, default=None):
            return self._params.get(key, default)

        def getParams(self):
            return self._params

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        if param == "TutorialFades":
            TutorialFadesManager.loadFades(records)
        elif param == "TutorialConfig":
            TutorialFadesManager.loadConfig(records)

        return True

    @staticmethod
    def loadFades(records):
        params = TutorialFadesManager.Fades(records)
        TutorialFadesManager.s_fades = params

    @staticmethod
    def loadConfig(records):
        params = TutorialFadesManager.Config(records)
        TutorialFadesManager.s_config = params

    @staticmethod
    def getFades():
        return TutorialFadesManager.s_fades

    @staticmethod
    def getConfig():
        return TutorialFadesManager.s_config

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
