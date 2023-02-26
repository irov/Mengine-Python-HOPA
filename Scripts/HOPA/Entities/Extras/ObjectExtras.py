from Foundation.Object.DemonObject import DemonObject

class ObjectExtras(DemonObject):
    def _onParams(self, params):
        super(ObjectExtras, self)._onParams(params)
        self.params["CurrentLayer"] = params.get("CurrentLayer", "ExtrasHOGs")
        self.params["OpenedExtraNames"] = params.get("OpenedExtraNames", [])
        pass
    pass