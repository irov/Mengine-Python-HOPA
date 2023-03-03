from Foundation.Object.DemonObject import DemonObject


class ObjectBonusVideo(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, "CurrentPageIndex")

    def _onParams(self, params):
        super(ObjectBonusVideo, self)._onParams(params)
        self.initParam("CurrentPageIndex", params, 0)
