from Foundation.Object.DemonObject import DemonObject


class ObjectOptionsMore(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("Arrow")
        Type.declareParam("WideScreen")
        pass

    def _onParams(self, params):
        super(ObjectOptionsMore, self)._onParams(params)

        self.initParam('Arrow', params, False)
        self.initParam('WideScreen', params, False)
        pass
