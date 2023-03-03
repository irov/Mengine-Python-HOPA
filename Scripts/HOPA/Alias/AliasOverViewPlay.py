from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias


class AliasOverViewPlay(MixinObject, TaskAlias):
    def _onParams(self, params):
        super(AliasOverViewPlay, self)._onParams(params)

        self.ViewID = params.get("ViewID")
        self.FinalParagraph = params.get("FinalParagraph", [])
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onOverView, Args=(self.ViewID, self.FinalParagraph))
