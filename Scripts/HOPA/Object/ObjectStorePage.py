from Foundation.Object.DemonObject import DemonObject


class ObjectStorePage(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addConst(Type, 'PageID')
        Type.addConst(Type, 'Scrollable')
        Type.addParam(Type, 'WaitButtons')

    def _onParams(self, params):
        super(ObjectStorePage, self)._onParams(params)
        self.initConst('PageID', params)
        self.initConst('Scrollable', params, False)
        self.initParam('WaitButtons', params, [])

    def hasNotify(self):
        return self.getEntity().hasNotify()
