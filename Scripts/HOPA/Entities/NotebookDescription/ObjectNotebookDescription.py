from Foundation.Object.Object import Object

class ObjectNotebookDescription(Object):
    def _onParams(self, params):
        super(ObjectNotebookDescription, self)._onParams(params)
        self.initParam("CurrentNote", params, None)
        pass

    pass