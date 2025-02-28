from Foundation.SceneManager import SceneManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyDialogDynamicTextPlay(TaskAlias):

    def __init__(self):
        super(PolicyDialogDynamicTextPlay, self).__init__()

        self.CleanScene = []
        pass

    def _onParams(self, params):
        super(PolicyDialogDynamicTextPlay, self)._onParams(params)

        self.ObjectText = params.get("ObjectText")
        self.TextID = params.get("TextID")
        self.TextDelay = params.get("TextDelay")
        self.AudioDuration = params.get("AudioDuration")
        pass

    def _onGenerate(self, source):
        self.ObjectText.setParam("TextID", None)
        source.addFunction(self.__AddToLayer, self.ObjectText, "Dialog")

        source.addTask("AliasTextPlay", ObjectText=self.ObjectText, TextID=self.TextID,
                       TextDelay=self.TextDelay, AudioDuration=self.AudioDuration)
        # source.addTask("TaskFunction", Fn=self.clearance)
        pass

    def __AddToLayer(self, MovieObj, LayerName):
        MovieObj.setEnable(True)
        self.CleanScene.append(MovieObj)
        Layer = SceneManager.getLayerScene(LayerName)
        MovieEnNode = MovieObj.getEntityNode()
        Layer.addChild(MovieEnNode)
        pass

    def clearance(self):
        for movie in self.CleanScene:
            movie.returnToParent()
            pass

        self.CleanScene = []
        pass
