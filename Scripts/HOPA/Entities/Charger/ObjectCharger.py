from Foundation.Object.DemonObject import DemonObject

class ObjectCharger(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addConst(Type, "ResourceMovieCharge")
        Type.addConst(Type, "ResourceMovieCharged")
        Type.addConst(Type, "ResourceMovieIdle")
        Type.addConst(Type, "ResourceMovieRelease")
        ###
        Type.addConst(Type, "ResourceMovieEnter")
        Type.addConst(Type, "ResourceMovieOver")
        Type.addConst(Type, "ResourceMovieLeave")

        Type.addParam(Type, "TimeReload")
        Type.addParam(Type, "WaitCharge")
        Type.addParam(Type, "NoCharge")
        Type.addParam(Type, "State")
        pass

    def _onParams(self, params):
        super(ObjectCharger, self)._onParams(params)

        self.initConst("ResourceMovieCharge", params)
        self.initConst("ResourceMovieCharged", params, None)
        self.initConst("ResourceMovieIdle", params)
        self.initConst("ResourceMovieRelease", params, None)

        self.initConst("ResourceMovieEnter", params, None)
        self.initConst("ResourceMovieOver", params, None)
        self.initConst("ResourceMovieLeave", params, None)

        self.initParam("TimeReload", params, 1000.0)
        self.initParam("WaitCharge", params, False)
        self.initParam("NoCharge", params, False)
        self.initParam("State", params, "Idle")
        pass

    pass