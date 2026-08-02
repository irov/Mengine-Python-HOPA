from Foundation.Object import Object

class ObjectNotebookDescription(Object):
    @staticmethod
    def declareORM(Type):
        Object.declareORM(Type)
        Type.declareParam("CurrentNote")

    def _onParams(self, params):
        super(ObjectNotebookDescription, self)._onParams(params)
        self.initParam("CurrentNote", params, None)
        pass

    pass
