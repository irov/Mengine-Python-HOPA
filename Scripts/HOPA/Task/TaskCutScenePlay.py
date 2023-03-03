from Foundation.DemonManager import DemonManager
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.TaskAlias import TaskAlias


class TaskCutScenePlay(MixinObserver, TaskAlias):
    def __init__(self):
        super(TaskCutScenePlay, self).__init__()

        self.NextCutScene = None

    def _onParams(self, params):
        super(TaskCutScenePlay, self)._onParams(params)

        self.CutSceneName = params.get("CutSceneName")
        self.CutSceneDemonName = params.get("CutSceneDemonName", "CutScene")
        self.CutSceneSceneName = params.get("CutSceneSceneName", "CutScene")
        self.Transition = params.get("Transition", True)
        self.isFade = params.get("isFade", True)

    def _onGenerate(self, source):
        demon_cut_scene = DemonManager.getDemon(self.CutSceneDemonName)

        if self.Transition is True:
            source.addTask("AliasTransition", SceneName=self.CutSceneSceneName)
        source.addTask("TaskSetParam", Object=demon_cut_scene, Param="isFade", Value=self.isFade)
        source.addTask("TaskSetParam", Object=demon_cut_scene, Param="CutSceneName", Value=self.CutSceneName)
        source.addTask("TaskSetParam", Object=demon_cut_scene, Param="Play", Value=True)

        def __this(cut_scene_name, next_scene=None):
            return cut_scene_name is self.CutSceneName

        source.addTask("TaskListener", ID=Notificator.onCutScenePlay, Filter=__this)
        source.addTask("TaskSetParam", Object=demon_cut_scene, Param="Play", Value=False)
