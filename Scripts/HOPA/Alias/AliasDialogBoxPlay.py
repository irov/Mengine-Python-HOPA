from Foundation.GuardBlockGame import GuardBlockGame
from Foundation.Task.TaskAlias import TaskAlias


class AliasDialogBoxPlay(TaskAlias):
    def _onParams(self, params):
        super(AliasDialogBoxPlay, self)._onParams(params)

        self.DialogID = params.get("DialogID")
        pass

    def _onGenerate(self, source):
        with GuardBlockGame(source) as tc:
            # tc.addTask("TaskDialogBoxPlay", DialogID=self.dialogID)
            tc.addNotify(Notificator.onDialogBoxShowRelease, self.DialogID)
            tc.addNotify(Notificator.onDialogBoxShow, self.DialogID)
            tc.addListener(Notificator.onDialogBoxPlayComplete)
            pass
        pass

    pass
