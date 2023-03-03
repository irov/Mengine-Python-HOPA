from Foundation.Object.DemonObject import DemonObject


class ObjectSkipPuzzle(DemonObject):
    def _onParams(self, params):
        super(ObjectSkipPuzzle, self)._onParams(params)
        self.initParam("ForceReload", params, None)
        pass

    pass
