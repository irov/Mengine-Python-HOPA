from HOPA.Macro.MacroCommand import MacroCommand

from HOPA.ZoomManager import ZoomManager

class MacroZoomInterrupt(MacroCommand):

    def _onInitialize(self):
        super(MacroZoomInterrupt, self)._onInitialize()

        if _DEVELOPMENT is True:
            if ZoomManager.hasZoom(self.GroupName) is False:
                self.initializeFailed("Invalid found Zoom %s" % (self.GroupName))

    def _onGenerate(self, source):
        source.addDelay(1000.0)
        source.addTask("TaskZoomClose", ZoomName=self.GroupName, SceneName=self.SceneName, Value=True)

        ZoomObject = ZoomManager.getZoomObject(self.GroupName)

        if ZoomObject is not None:
            source.addTask("TaskEnable", Object=ZoomObject, Value=False)
            source.addFunction(ZoomObject.setEnd, True)