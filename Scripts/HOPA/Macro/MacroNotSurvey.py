# coding=utf-8
from Foundation.Utils import isSurvey
from HOPA.Macro.MacroCommand import MacroCommand

class MacroNotSurvey(MacroCommand):

    def _onValues(self, values):
        self.ParagraphsID = values

    def _onGenerate(self, source):
        if isSurvey() is True:
            source.addDummy()
            return

        for paragraphID in self.ParagraphsID:
            self.__runParagraph(source, paragraphID)

    def __runParagraph(self, source, paragraphID):
        if paragraphID is None or paragraphID == "":
            Trace.log("Command", 0, "MacroIsSurvey paragraphID is invalid '%s'" % (paragraphID))
            return

        Quest = self.addQuest(source, "RunParagraph", SceneName=self.SceneName, GroupName=self.GroupName, ParagraphsID=self.ParagraphsID)

        with Quest as tc_quest:
            # tc_quest.addTask("TaskPrint", Value = "RunParagraph %s:%s"%(paragraphID, self.GroupName))
            tc_quest.addTask("TaskNotify", ID=Notificator.onParagraphRun, Args=(paragraphID,))