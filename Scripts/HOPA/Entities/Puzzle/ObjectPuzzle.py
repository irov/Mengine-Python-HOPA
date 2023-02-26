from HOPA.Object.ObjectEnigma import ObjectEnigma

class ObjectPuzzle(ObjectEnigma):
    def _onParams(self, params):
        super(ObjectPuzzle, self)._onParams(params)
        self.initParam("PlacedItems", params, [])
        pass

    pass