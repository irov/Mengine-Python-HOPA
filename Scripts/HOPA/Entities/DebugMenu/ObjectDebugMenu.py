from Foundation.Object.DemonObject import DemonObject


class ObjectDebugMenu(DemonObject):
    def _onParams(self, params):
        super(ObjectDebugMenu, self)._onParams(params)
        self.initParam("Font", params, None)
        self.initParam("Zoom", params, None)
