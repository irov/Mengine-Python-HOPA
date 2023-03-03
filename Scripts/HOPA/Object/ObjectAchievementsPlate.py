from Foundation.Object.DemonObject import DemonObject


class ObjectAchievementsPlate(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addParam(Type, "AchievementsQueue")

    def _onParams(self, params):
        super(ObjectAchievementsPlate, self)._onParams(params)
        self.initParam("AchievementsQueue", params, [])

    def popParam(self, param_name):
        list_ = self.getParam(param_name)
        if len(list_) == 0:
            return
        el = list_.pop(0)
        self.setParam(param_name, list_)
        return el
