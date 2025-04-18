from Functor import Functor
from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.StageManager import StageManager


class MacroWaitParagraph(MacroCommand):
    def _onValues(self, values):
        self.Paragraphs = values

    def _onInitialize(self):
        self.isTechnical = True

        if _DEVELOPMENT is True:
            for Paragraph in self.Paragraphs:
                if StageManager.hasStage(Paragraph) is True:
                    continue

                if Paragraph[:3] == "PH_":
                    continue

                self.initializeFailed("Paragraph invalid %s" % (Paragraph))

    def _onGenerate(self, source):
        Quest = self.addQuest(source, "WaitParagraph", SceneName=self.SceneName,
                              GroupName=self.GroupName, Paragraphs=self.Paragraphs)

        with Quest as tc_quest:
            with tc_quest.addParallelTask(len(self.Paragraphs)) as tcp_paragraphs:
                for tci, paragraphID in zip(tcp_paragraphs, self.Paragraphs):
                    tci.addScope(self._scopeGenerate, paragraphID)

    def _scopeGenerate(self, source, paragraphID):
        def __isParagraphComplete(isSkip, cb, id):
            if self.ScenarioChapter.isParagraphComplete(id) is True:
                cb(isSkip, 1)
                return
            cb(isSkip, 0)

        def __paragraphFilter(paragraphID, id):
            if id != paragraphID:
                return False
            return True

        if StageManager.hasStage(paragraphID) is True:
            source.addTask("TaskStageInit", StageName=paragraphID)
        else:
            with source.addSwitchTask(2, Functor(__isParagraphComplete, paragraphID)) as (listener, skip):
                listener.addListener(Notificator.onParagraphRun, Filter=Functor(__paragraphFilter, paragraphID))
