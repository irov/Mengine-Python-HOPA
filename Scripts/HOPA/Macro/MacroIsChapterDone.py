from HOPA.Entities.Map2.Map2Manager import Map2Manager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroIsChapterDone(MacroCommand):
    def _onValues(self, values):
        if len(values) == 1:
            self.MindID = values[0]
        else:
            self.MindID = None
        pass

    def _onGenerate(self, source):
        source.addScope(self.scopeAllWork)

    def scopeAllWork(self, source):
        allScenesIsDone = Map2Manager.AllScenesIsDone()
        if allScenesIsDone:
            source.addNotify(Notificator.onChapterDone)
        else:
            if self.MindID is not None:
                source.addTask("AliasMindPlay", MindID=self.MindID, isZoom=False, Static=False)
