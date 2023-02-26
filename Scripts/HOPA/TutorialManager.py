from Foundation.DatabaseManager import DatabaseManager
from TraceManager import TraceManager

class TutorialManager(object):
    TraceName = "TutorialManager"
    s_object = {}

    class TutorialEntry(object):
        def __init__(self, movieName, textID):
            self.movie = movieName
            self.textId = textID
            pass

        def getMovieName(self):
            return self.movie
            pass

        def getText(self):
            return self.textId
            pass

        def __repr__(self):
            # for print debug
            return self.__dict__.__repr__()
            pass

    @staticmethod
    def onFinalize():
        TutorialManager.s_items = {}
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
        pass
    #        print TutorialManager.s_object

    @staticmethod
    def hasEntry(Name):
        if Name in TutorialManager.s_object:
            return True
        else:
            return False
        pass

    @staticmethod
    def getMovieName(Name):
        if TutorialManager.hasEntry(Name) is False:
            Trace.log(TutorialManager.TraceName, 0, "TutorialManager: name-key %s doest exist" % Name)
            return
            pass

        tutorialEntry = TutorialManager.s_object[Name]
        movieName = tutorialEntry.getMovieName()
        return movieName
        pass

    @staticmethod
    def getText(Name):
        if TutorialManager.hasEntry(Name) is False:
            Trace.log(TutorialManager.TraceName, 0, "TutorialManager: name-key %s doest exist" % Name)
            return
            pass

        tutorialEntry = TutorialManager.s_object[Name]
        text = tutorialEntry.getText()
        return text
        pass