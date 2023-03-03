from Foundation.DemonManager import DemonManager
from Foundation.System import System
from Notification import Notification


class SystemJournal2(System):

    def __init__(self):
        super(SystemJournal2, self).__init__()
        self.onJournalAddObserver = None
        pass

    def _onRun(self):
        self.onJournalAddObserver = Notification.addObserver(Notificator.onJournalAddPage, self.__onJournalAdd)
        return True
        pass

    def __onJournalAdd(self, journalID):
        Journal = DemonManager.getDemon("Journal")
        Journal.appendParam("OpenPages", journalID)
        return False
        pass

    def _onStop(self):
        Notification.removeObserver(self.onJournalAddObserver)
        pass

    pass
