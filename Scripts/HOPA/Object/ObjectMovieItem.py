from Foundation.Object.DemonObject import DemonObject


class ObjectMovieItem(DemonObject):
    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addConst(Type, "ResourceMovieIdle")
        Type.addConst(Type, "ResourceMoviePick")
        pass

    def _onParams(self, params):
        super(ObjectMovieItem, self)._onParams(params)
        self.initConst("ResourceMovieIdle", params)
        self.initConst("ResourceMoviePick", params, None)
        pass

    pass
