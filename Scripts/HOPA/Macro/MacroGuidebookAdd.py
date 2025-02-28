from HOPA.Entities.Journal2.Journal2Manager import Journal2Manager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroGuidebookAdd(MacroCommand):
    def _onValues(self, values):
        self.ObjectName = None
        self.GuidebookID = values[0]

        if len(values) < 2:
            return
            pass

        self.ObjectName = values[1]
        pass

    def _onInitialize(self, **params):
        if _DEVELOPMENT is True:
            if Journal2Manager.hasPage(self.GuidebookID) is False:
                self.initializeFailed("GuidebookPage ->%s is not registered.Please add item to appropriate places" % (self.JournalID))

    def _onGenerate(self, source):
        if self.ObjectName is not None:
            source.addTask("AliasObjectClick", ObjectName=self.ObjectName, SceneName=self.SceneName)
            source.addTask("TaskEnable", ObjectName=self.ObjectName, Value=False)
            pass

        source.addNotify(Notificator.onGuidebookAddPage, self.GuidebookID)
        pass

    pass
