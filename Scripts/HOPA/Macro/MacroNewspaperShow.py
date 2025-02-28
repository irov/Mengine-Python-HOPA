from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.NewspaperManager import NewspaperManager
from HOPA.StageManager import StageManager


class MacroNewspaperShow(MacroCommand):
    def _onValues(self, values):
        self.NewspaperName = values[0]
        self.ParagraphsID = values[1:]
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
        def __idFilter(NewspaperName):
            if NewspaperName != self.NewspaperName:
                return False
                pass

            return True
            pass

        if NewspaperManager.hasNewspaper(self.NewspaperName) is False:
            Trace.log("Entity", 0, "MacroNewspaperShow not found newspaper ID %s" % (self.NewspaperName))
            return
            pass

        newspaper = NewspaperManager.getNewspaper(self.NewspaperName)
        clickObject = newspaper.socket_Open

        Quest = self.addQuest(source, "Newspaper", SceneName=self.SceneName, GroupName=self.GroupName,
                              Object=clickObject)

        with Quest as tc_quest:
            with tc_quest.addIfTask(NewspaperManager.isOpenNewspaper, self.NewspaperName) as (tc_quest_yes, tc_quest_no):
                tc_quest_no.addListener(Notificator.onNewspaperOpen, Filter=__idFilter)

                for ParagraphID in self.ParagraphsID:
                    tc_quest_no.addNotify(Notificator.onParagraphRun, ParagraphID)
                    pass

                tc_quest_no.addListener(Notificator.onNewspaperShow, Filter=__idFilter)
                pass
            pass
        pass

    pass
