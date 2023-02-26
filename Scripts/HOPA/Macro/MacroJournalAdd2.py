from HOPA.Entities.Journal2.Journal2Manager import Journal2Manager
from HOPA.Macro.MacroCommand import MacroCommand

class MacroJournalAdd2(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = None
        self.JournalID = values[0]

        if len(values) < 2:
            return
            pass

        self.ObjectName = values[1]
        pass

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if Journal2Manager.hasPage(self.JournalID) is False:
                self.initializeFailed("JournalPage ->%s is not registered.Please add item to appropriate places" % (self.JournalID))
                pass
            pass
        pass

    def _onGenerate(self, source):
        if self.ObjectName is not None:
            source.addTask("AliasObjectClick", ObjectName=self.ObjectName, SceneName=self.SceneName)
            source.addTask("TaskEnable", ObjectName=self.ObjectName, Value=False)
            pass

        source.addTask("TaskNotify", ID=Notificator.onJournalAddPage, Args=(self.JournalID,))
        pass
    pass