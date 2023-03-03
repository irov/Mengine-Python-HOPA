from HOPA.Entities.Map2.Map2Manager import Map2Manager
from HOPA.Macro.MacroCommand import MacroCommand


class MacroChapterComplete(MacroCommand):

    def _onValues(self, values):
        self.isTechnical = True

    def _scopeIsChapterAlreadyDone(self, source):
        if Map2Manager.AllScenesIsDone() is True:
            source.addNotify(Notificator.onChapterDone)

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "TechnicalQuest", SceneName=self.SceneName, GroupName=self.GroupName)

        with Quest as tc_quest:
            with tc_quest.addParallelTask(2) as (tc_wait_done, tc_already_done):
                tc_wait_done.addListener(Notificator.onChapterDone)
                tc_already_done.addScope(self._scopeIsChapterAlreadyDone)
