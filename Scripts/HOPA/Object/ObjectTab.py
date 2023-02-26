from Foundation.Object.DemonObject import DemonObject

class ObjectTab(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "Tabs")
        Type.addParam(Type, "CurrentTab")
        pass

    def _onParams(self, params):
        super(ObjectTab, self)._onParams(params)
        self.initParam("Tabs", params, {})
        self.initParam("CurrentTab", params, None)
        pass
    pass