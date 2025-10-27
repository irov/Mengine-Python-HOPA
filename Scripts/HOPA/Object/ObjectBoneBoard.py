from Foundation.Object.DemonObject import DemonObject


class ObjectBoneBoard(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareParam("HelperState")
        Type.declareParam("BoneActivities")
        Type.declareParam("ButtonAvailable")
        Type.declareParam("UseAvailable")
        pass

    def _onParams(self, params):
        super(ObjectBoneBoard, self)._onParams(params)
        self.initParam("HelperState", params, False)
        self.initParam("BoneActivities", params, [])
        self.initParam("ButtonAvailable", params, False)
        self.initParam("UseAvailable", params, {})
        pass

    def removeAllData(self):
        self.setParam("HelperState", False)
        self.setParam("BoneActivities", [])
        self.setParam("ButtonAvailable", False)
        self.setParam("UseAvailable", {})
        pass

    pass
