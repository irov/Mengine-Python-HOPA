from Foundation.Object.DemonObject import DemonObject


class ObjectCharger(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.declareConst("ResourceMovieCharge")
        Type.declareConst("ResourceMovieCharged")
        Type.declareConst("ResourceMovieIdle")
        Type.declareConst("ResourceMovieRelease")
        ###
        Type.declareConst("ResourceMovieEnter")
        Type.declareConst("ResourceMovieOver")
        Type.declareConst("ResourceMovieLeave")

        Type.declareParam("TimeReload")
        Type.declareParam("WaitCharge")
        Type.declareParam("NoCharge")
        Type.declareParam("State")
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
