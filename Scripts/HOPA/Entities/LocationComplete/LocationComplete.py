from Foundation.Entity.BaseEntity import BaseEntity
# from Foundation.SceneManager import SceneManager
# from Foundation.TaskManager import TaskManager


class LocationComplete(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        # Type.addAction("CompleteScenes", Append=LocationComplete._appendCompleteScenes)
        Type.addAction("CompleteScenes")

    def __init__(self):
        super(LocationComplete, self).__init__()
        # self.timeClick = []
        # self.LocationCompleteCountClick = DefaultManager.getDefaultFloat("LocationCompleteCountClick", 5)
        # self.LocationCompleteCountClick = 5

    def _onPreparation(self):
        self.text = self.object.getObject("Sprite_Text")
        self.text.setEnable(False)

        self.back = self.object.getObject("Sprite_Back")
        self.back.setEnable(False)

    # def _onDeactivate(self):
    #     self.text.setEnable(False)
    #     self.back.setEnable(False)

    # def _appendCompleteScenes(self, id, sceneName):
    #     currentSceneName = SceneManager.getCurrentSceneName()
    #
    # if sceneName == currentSceneName:
    #
    #     self._startClick()

    #     currentSceneName = SceneManager.getCurrentSceneName()
    #     CompleteScenes = self.object.getParam("CompleteScenes")
    #     if currentSceneName in CompleteScenes:
    #         self._startClick()
    #
    # def _startClick(self):
    #     if TaskManager.existTaskChain("LocationCompleteClick"):
    #         return
    #
    #     with TaskManager.createTaskChain(Name="LocationCompleteClick", Repeat=True) as tc:
    #
    # tc.addTask("TaskMouseButtonClick")
    #         tc.addTask("TaskFunction", Fn=self._addTimeClick)

    # def _addTimeClick(self):
    #
    # time = Mengine.getTime()
    #     # self.timeClick.append(time)
    #
    #
    #
    # if len(self.timeClick) < self.LocationCompleteCountClick:
    #
    #     return
    #
    #
    #
    # currentTime = self.timeClick[-1]
    #
    #
    #
    # for time in self.timeClick[-1:-self.LocationCompleteCountClick:-1]:
    #
    #
    #
    #     LocationCompleteTimeWait = DefaultManager.getDefaultFloat("LocationCompleteTimeWait", 0.0)
    #
    #     LocationCompleteTimeWait *= 1000  # speed fix
    #
    #     if currentTime - time < LocationCompleteTimeWait:
    #
    #         continue
    #
    #
    #
    #     return
    #
    #     self.text.setEnable(True)
    #     self.back.setEnable(True)
    #     TaskManager.cancelTaskChain("LocationCompleteClick")
