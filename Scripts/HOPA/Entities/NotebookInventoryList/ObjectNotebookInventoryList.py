from Foundation.Object.DemonObject import DemonObject

class ObjectNotebookInventoryList(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "OpenNotes")
        pass

    def _onParams(self, params):
        super(ObjectNotebookInventoryList, self)._onParams(params)
        self.initParam("OpenNotes", params, [])
        pass

    pass