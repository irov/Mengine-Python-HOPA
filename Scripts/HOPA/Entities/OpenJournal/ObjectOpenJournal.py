from Foundation.Object.DemonObject import DemonObject

class ObjectOpenJournal(DemonObject):
    def _onParams(self, params):
        super(ObjectOpenJournal, self)._onParams(params)
        self.initParam("State", params, "Static")
        pass
    pass