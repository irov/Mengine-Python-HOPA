from HOPA.Macro.MacroCommand import MacroCommand


class MacroIsTrial(MacroCommand):
    def _onValues(self, values):
        self.ParagraphsID = values
        pass

    def _onGenerate(self, source):
        if Mengine.getGameParamUnicode("BuildModeCheckVersion") == u"2.0":
            if Mengine.getGameParamUnicode("BuildMode") != u"Trial":
                source.addDummy()
                return
        else:
            source.addDummy()
            return

        for paragraphID in self.ParagraphsID:
            self.__runParagraph(source, paragraphID)
            pass
        pass

    def __runParagraph(self, source, paragraphID):
        if paragraphID is None or paragraphID == "":
            Trace.log("Command", 0, "MacroIsTrial paragraphID is invalid '%s'" % (paragraphID))
            return
            pass

        Quest = self.addQuest(source, "RunParagraph", SceneName=self.SceneName, GroupName=self.GroupName,
                              ParagraphsID=self.ParagraphsID)

        with Quest as tc_quest:
            # tc_quest.addTask("TaskPrint", Value = "RunParagraph %s:%s"%(paragraphID, self.GroupName))
            tc_quest.addTask("TaskNotify", ID=Notificator.onParagraphRun, Args=(paragraphID,))
