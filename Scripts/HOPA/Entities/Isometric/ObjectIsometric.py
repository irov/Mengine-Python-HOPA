from Foundation.Object.Object import Object

class ObjectIsometric(Object):
    def _onParams(self, params):
        super(ObjectIsometric, self)._onParams(params)

        self.initConst("Animations", params, None)
        pass
    pass