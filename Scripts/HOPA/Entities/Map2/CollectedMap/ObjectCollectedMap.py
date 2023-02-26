from Foundation.Object.DemonObject import DemonObject

class ObjectCollectedMap(DemonObject):
    def _onParams(self, params):
        super(ObjectCollectedMap, self)._onParams(params)
        self.initParam("OpenParts", params, [])
        pass
    pass