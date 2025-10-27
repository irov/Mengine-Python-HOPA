from Foundation.Object.DemonObject import DemonObject


class ObjectTab(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Tabs")
        Type.declareParam("CurrentTab")
        pass

    def _onParams(self, params):
        super(ObjectTab, self)._onParams(params)
        self.initParam("Tabs", params, {})
        self.initParam("CurrentTab", params, None)
        pass

    pass
