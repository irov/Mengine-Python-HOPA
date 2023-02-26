from Foundation.Object.DemonObject import DemonObject

class ObjectWalktrhoughText(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "Open")
        pass

    def _onParams(self, params):
        super(ObjectWalktrhoughText, self)._onParams(params)
        self.initParam("Open", params, False)
        pass
    pass