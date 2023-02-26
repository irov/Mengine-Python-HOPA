from Foundation.Object.DemonObject import DemonObject

class ObjectNewspaper(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "NewspaperID")
        Type.addParam(Type, "Open")
        Type.addParam(Type, "ShowComplete")
        pass

    def _onParams(self, params):
        super(ObjectNewspaper, self)._onParams(params)

        self.initParam("NewspaperID", params, None)
        self.initParam("Open", params, False)
        self.initParam("ShowComplete", params, False)
        pass
    pass