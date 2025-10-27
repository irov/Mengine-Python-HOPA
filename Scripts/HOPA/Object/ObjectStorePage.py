from Foundation.Object.DemonObject import DemonObject


class ObjectStorePage(DemonObject):

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addConst(Type, 'PageID')
        Type.addConst(Type, 'Scrollable')
        Type.addConst(Type, 'ScrollMode')
        Type.declareParam('WaitButtons')

        Type.declareConst("ColumnsCount")
        Type.declareConst("OffsetY")
        Type.declareConst("AllowArrow")

    def _onParams(self, params):
        super(ObjectStorePage, self)._onParams(params)
        self.initConst('PageID', params)
        self.initConst('Scrollable', params, False)
        self.initConst('ScrollMode', params, 'horizontal')
        self.initParam('WaitButtons', params, [])

        self.initConst("ColumnsCount", params, 1)
        self.initConst("OffsetY", params, 0)
        self.initConst("AllowArrow", params, False)

    def hasNotify(self):
        return self.getEntity().hasNotify()
