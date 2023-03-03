from Foundation.DefaultManager import DefaultManager
from Foundation.Object.DemonObject import DemonObject


class ObjectHint(DemonObject):
    ACTION_EMPTY_USE = 0
    ACTION_REGULAR_USE = 1
    ACTION_MIND_USE = 2
    ACTION_NO_RELOAD_USE = 3

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)

        Type.addParam(Type, "Point")
        Type.addParam(Type, "ZoomCheck")
        Type.addParam(Type, "ItemCollectCheck")
        Type.addParam(Type, "AroundSceneCheck")
        pass

    def _onParams(self, params):
        super(ObjectHint, self)._onParams(params)

        self.initParam("Point", params, (0.0, 0.0))
        self.initParam("ZoomCheck", params, False)
        self.initParam("ItemCollectCheck", params, False)
        self.initParam("AroundSceneCheck", params, False)
        pass

    def getGroup(self):
        MovieHintInDemon = DefaultManager.getDefaultBool("MovieHintInDemon", False)
        if MovieHintInDemon is True:
            MovieGroup = self
            pass
        else:
            MovieGroup = self.Group
            pass

        return MovieGroup
        pass

    pass
