from Foundation.Object.DemonObject import DemonObject


class ObjectNotebookInventory(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareParam("OpenNotes")
        Type.declareParam("CloseNotes")

    def _onParams(self, params):
        super(ObjectNotebookInventory, self)._onParams(params)
        self.initParam("OpenNotes", params, [])
        self.initParam("CloseNotes", params, [])
