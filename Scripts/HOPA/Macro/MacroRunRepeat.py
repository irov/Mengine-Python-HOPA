from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.StageManager import StageManager

class MacroRunRepeat(MacroCommand):
    def _onValues(self, values):
        self.ParagraphsID = values
        pass

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            for paragraphID in self.ParagraphsID:
                if StageManager.hasStage(paragraphID) is True:
                    continue
                    pass

                if paragraphID[:3] != "PH_":
                    self.initializeFailed("%s:%d Paragraph %s invalid - 'PH_'" % (self.getGroupName(), self.getIndex(), paragraphID))
                    pass
                pass
            pass
        pass

    def _onGenerate(self, source):
        for paragraphID in self.ParagraphsID:
            self.__runParagraph(source, paragraphID)
            pass
        pass

    def __runParagraph(self, source, paragraphID):
        if paragraphID is None or paragraphID == "":
            Trace.log("Command", 0, "MacroRunRepeat paragraphID is invalid '%s'" % (paragraphID))
            return
            pass

        source.addTask("TaskNotify", ID=Notificator.onParagraphRun, Args=(paragraphID,))
        pass
    pass