from Foundation.Object.DemonObject import DemonObject
from Foundation.TaskManager import TaskManager


class ObjectAdvertisingScene(DemonObject):

    transition_data = None
    ignore_scenes = ["CutScene", "Dialog"]

    @staticmethod
    def declareORM(Type):
        DemonObject.declareORM(Type)
        Type.addConst(Type, "AdvertSceneName")
        Type.addParam(Type, "CacheNoAds")

    def _onParams(self, params):
        super(ObjectAdvertisingScene, self)._onParams(params)
        self.initConst("AdvertSceneName", params, "Advertising")
        self.initParam("CacheNoAds", params, False)

    def setTransitionData(self, data):
        self.transition_data = data.copy()
        print "******* setTransitionData", data

    def runNextTransition(self):
        """ do transition on next scene as planned """
        print "******* runNextTransition"
        if self.transition_data is not None:
            TaskManager.runAlias("AliasTransition", None, **self.transition_data)
            return True

        Trace.log("Object", 0, "Can't do next transition - transition data is None")
        return False

    def runAdvertTransition(self):
        """ do transition on advert scene if True, else (if False) - make default transition """
        print "******* runAdvertTransition"

        if self.transition_data is None:
            Trace.log("Object", 0, "You forgot to set transition data!!!!!!")
            return False

        if self.getParam("CacheNoAds") is True:
            print "!!!!!!!!!!!!!! no ads"
            return False

        if self.transition_data.get("SceneName") in self.ignore_scenes:
            print "!!!!!!!!!!!!!! SceneName", self.transition_data.get("SceneName"), "in", self.ignore_scenes
            return False

        MovieIn = self.transition_data.pop("MovieIn", None)
        ZoomEffectTransitionObject = self.transition_data.pop("ZoomEffectTransitionObject", None)

        TaskManager.runAlias("AliasTransition", None, SceneName="Advertising",
                             MovieIn=MovieIn, ZoomEffectTransitionObject=ZoomEffectTransitionObject)
        return True



