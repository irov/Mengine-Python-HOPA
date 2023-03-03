from Foundation.Object.DemonObject import DemonObject


class ObjectReloader(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addResource(Type, "ResourceMovieIdle")
        Type.addResource(Type, "ResourceMovieBegin")
        Type.addResource(Type, "ResourceMovieProcess")
        Type.addResource(Type, "ResourceMovieEnd")

        Type.addParam(Type, "Time")
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
