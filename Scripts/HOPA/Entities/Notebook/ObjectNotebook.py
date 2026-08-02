from Foundation.DemonObject import DemonObject


class ObjectNotebook(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam("OpenNotes")
        Type.declareParam("CloseNotes")
        Type.declareParam("CurrentNote")
        Type.declareParam("CurrentPageID")
        Type.declareParam("PageSize")

    def _onParams(self, params):
        super(ObjectNotebook, self)._onParams(params)
        self.initParam("OpenNotes", params, [])
        self.initParam("CloseNotes", params, [])
        self.initParam("CurrentNote", params, None)
        self.initParam("CurrentPageID", params, 0)
        self.initParam("PageSize", params, 1)
        pass

    pass
