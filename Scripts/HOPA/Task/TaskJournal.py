from Foundation.Task.Task import Task
from Notification import Notification

class TaskJournal(Task):
    Skiped = True
    def _onParams(self, params):
        super(TaskJournal, self)._onParams(params)
        self.JournalID = params.get("JournalID")
        self.Journal = params.get("Journal")
        pass

    def _onRun(self):
        Pages = self.Journal.getParam("Pages")

        if self.JournalID in Pages:
            self.log("Journal already has this ID %s" % self.JournalID)
            return True
            pass

        self.Journal.appendParam("Pages", self.JournalID)

        Notification.notify(Notificator.onJournalAppendPage)

        return True
        pass

    pass