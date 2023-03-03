from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.OverViewManager import OverViewManager


class MacroOverView(MacroCommand):
    def _onValues(self, values):
        self.ViewID = values[0]
        #        self.ObjectName = values[0]
        self.FinalParagraphIDs = [value for value in values[1:] if value is not None]
        self.MouseEnter = None
        self.myObject = None
        self.HasID = True
        pass

    def _onInitialize(self):
        self.HasID = OverViewManager.hasView(self.ViewID)
        if self.HasID is False:
            #            self.initializeFailed("MacroOverView %s not found"%(self.ObjectName))
            pass
        pass

    def _onGenerate(self, source):
        if self.HasID is False:
            source.addTask("TaskPrint", Value="Missed %s" % (self.ViewID,))  # for Andromeda
        else:
            source.addTask("AliasOverViewPlay", ObjectName=self.ViewID, ViewID=self.ViewID,
                           FinalParagraph=self.FinalParagraphIDs)
        pass

    pass
