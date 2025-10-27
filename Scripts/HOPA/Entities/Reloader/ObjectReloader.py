from Foundation.Object.DemonObject import DemonObject


class ObjectReloader(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.declareResource("ResourceMovieIdle")
        Type.declareResource("ResourceMovieBegin")
        Type.declareResource("ResourceMovieProcess")
        Type.declareResource("ResourceMovieEnd")

        Type.declareParam("Time")
        pass

    def _onParams(self, params):
        super(ObjectReloader, self)._onParams(params)

        self.initResource("ResourceMovieIdle", params, None)
        self.initResource("ResourceMovieBegin", params, None)
        self.initResource("ResourceMovieProcess", params)
        self.initResource("ResourceMovieEnd", params, None)

        self.initParam("Time", params, 1000.0)
        pass

    pass
