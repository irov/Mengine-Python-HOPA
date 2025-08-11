from Foundation.Manager import Manager

from Foundation.DatabaseManager import DatabaseManager
from TraceManager import TraceManager

class TutorialManager(Manager):
    TraceName = "TutorialManager"
    s_object = {}

    class TutorialEntry(object):
        def __init__(self, movieName, textID):
            self.movie = movieName
            self.textId = textID

        def getMovieName(self):
            return self.movie

        def getText(self):
            return self.textId

        def __repr__(self):
            # for print debug
            return self.__dict__.__repr__()

    @staticmethod
    def _onFinalize():
        TutorialManager.s_object = {}
        pass

    @staticmethod
    def load(module, param):
        TraceManager.addTrace(TutorialManager.TraceName)
        records = DatabaseManager.getDatabaseRecords(module, param)
        for record in records:
            Key = record.get("Name")
            MovieName = record.get("Movie")
            TextID = record.get("TextID")
            TutorialManager.s_object[Key] = TutorialManager.TutorialEntry(MovieName, TextID)

    @staticmethod
    def hasEntry(Name):
        if Name in TutorialManager.s_object:
            return True
        else:
            return False

    @staticmethod
    def getMovieName(Name):
        if TutorialManager.hasEntry(Name) is False:
            Trace.log(TutorialManager.TraceName, 0, "TutorialManager: name-key %s doest exist" % Name)
            return

        tutorialEntry = TutorialManager.s_object[Name]
        movieName = tutorialEntry.getMovieName()
        return movieName

    @staticmethod
    def getText(Name):
        if TutorialManager.hasEntry(Name) is False:
            Trace.log(TutorialManager.TraceName, 0, "TutorialManager: name-key %s doest exist" % Name)
            return

        tutorialEntry = TutorialManager.s_object[Name]
        text = tutorialEntry.getText()
        return text
