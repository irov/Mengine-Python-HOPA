from Foundation.DatabaseManager import DatabaseManager
from Foundation.Manager import Manager


class MagicGloveManager(Manager):
    s_Button = {}

    @staticmethod
    def loadParams(module, param):
        records = DatabaseManager.getDatabaseRecords(module, param)

        for record in records:
            movie_button_name = record.get("MovieButtonName")
            state = record.get("State")
            MagicGloveManager.s_Button[state] = movie_button_name
        return True

    @staticmethod
    def getButtonName(state):
        return MagicGloveManager.s_Button.get(state, None)

    @staticmethod
    def getButtonNames():
        return MagicGloveManager.s_Button
