from Foundation.Object.Object import Object

class ObjectNotebookInventory(Object):
    def _onParams(self, params):
        super(ObjectNotebookInventory, self)._onParams(params)
        self.initParam("OpenNotes", params, [])
        self.initParam("CloseNotes", params, [])