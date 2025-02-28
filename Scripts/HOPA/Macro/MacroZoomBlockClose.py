from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.ZoomManager import ZoomManager


class MacroZoomBlockClose(MacroCommand):
    def _onValues(self, values):
        self.ZoomName = None

        if len(values) > 0:
            self.ZoomName = values[0]
            pass
        pass

    def _onInitialize(self):
        super(MacroZoomBlockClose, self)._onInitialize()
        if self.ZoomName is None:
            self.ZoomName = self.GroupName
            pass

        if _DEVELOPMENT is True:
            if ZoomManager.hasZoom(self.ZoomName) is False:
                self.initializeFailed("Invalid found Zoom %s" % (self.ZoomName,))
                pass
            pass
        pass

    def _onGenerate(self, source):
        source.addNotify(Notificator.onZoomBlockClose, self.ZoomName, True)
