from Foundation.Object.DemonObject import DemonObject

class ObjectDebugMenu(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Font")
        Type.declareParam("Zoom")
        pass

    def _onParams(self, params):
        super(ObjectDebugMenu, self)._onParams(params)

        self.initParam("Font", params, None)
        self.initParam("Zoom", params, None)
        pass