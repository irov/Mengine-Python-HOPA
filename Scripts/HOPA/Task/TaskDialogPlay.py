from Foundation.GroupManager import GroupManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task
from HOPA.DialogManager import DialogManager


class TaskDialogPlay(MixinObserver, Task):
    Skiped = False

    def __init__(self):
        super(TaskDialogPlay, self).__init__()

        self.Dialog = None
        pass

    def _onParams(self, params):
        super(TaskDialogPlay, self)._onParams(params)

        self.DialogID = params.get("DialogID")
        pass

    def _onInitialize(self):
        super(TaskDialogPlay, self)._onInitialize()

        if _DEVELOPMENT is True:
            if DialogManager.hasDialog(self.DialogID) is False:
                self.initializeFailed("Dialog %s not found" % (self.DialogID))
                pass

            dialogs = DialogManager.getDialogChain(self.DialogID)

            for dialog in dialogs:
                if Mengine.existText(dialog.textID) is False:
                    self.initializeFailed("Dialog '%s' invalid TextID '%s'" % (self.DialogID, dialog.textID))
                    pass
                pass
            pass

        dialog = DialogManager.getDialog(self.DialogID)
        self.Dialog = GroupManager.getObject(dialog.group, "Demon_Dialog")
        # self.Dialog = DemonManager.getDemon("Dialog")
        pass

    def _onRun(self):
        DialogManager.dialogShow(self.DialogID)

        def __onDialogCloseFilter(dialogID, dialog):
            return True
            pass

        self.addObserverFilter(Notificator.onDialogHide, __onDialogCloseFilter, self.DialogID)

        return False
        pass

    pass
