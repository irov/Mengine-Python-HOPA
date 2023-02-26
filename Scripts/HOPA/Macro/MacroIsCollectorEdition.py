from Foundation.Utils import isCollectorEdition
from HOPA.Macro.MacroCommand import MacroCommand

class MacroIsCollectorEdition(MacroCommand):

    def _onValues(self, values):
        self.ParagraphsID = values

    def __isCollectorEdition(self):
        return isCollectorEdition()

    def _onGenerate(self, source):
        if self.__isCollectorEdition() is False:
            source.addDummy()
            return

        for paragraphID in self.ParagraphsID:
            self.__runParagraph(source, paragraphID)

    def __runParagraph(self, source, paragraphID):
        if paragraphID is None or paragraphID == "":
            Trace.log("Command", 0, "MacroIsCollectorEdition paragraphID is invalid '%s'" % paragraphID)
            return

        Quest = self.addQuest(source, "RunParagraph", SceneName=self.SceneName, GroupName=self.GroupName, ParagraphsID=self.ParagraphsID)

        with Quest as tc_quest:
            tc_quest.addNotify(Notificator.onParagraphRun, paragraphID)