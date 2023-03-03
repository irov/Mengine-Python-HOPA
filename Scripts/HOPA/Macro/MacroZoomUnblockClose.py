from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.ZoomManager import ZoomManager


class MacroZoomUnblockClose(MacroCommand):
    def _onInitialize(self):
        super(MacroZoomUnblockClose, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ZoomManager.hasZoom(self.GroupName) is False:
                self.initializeFailed("Invalid found Zoom %s" % (self.GroupName,))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addTask("TaskNotify", ID=Notificator.onZoomBlockClose, Args=(self.GroupName, False))
