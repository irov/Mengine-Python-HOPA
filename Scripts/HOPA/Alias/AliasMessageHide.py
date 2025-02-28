from Foundation.GroupManager import GroupManager
from Foundation.GuardBlockInput import GuardBlockInput
from Foundation.Task.TaskAlias import TaskAlias


class AliasMessageHide(TaskAlias):
    def _onParams(self, params):
        super(AliasMessageHide, self)._onParams(params)

        self.SceneName = params.get("SceneName")
        pass

    def _onInitialize(self):
        super(AliasMessageHide, self)._onInitialize()
        pass

    def SceneEffect(self, source, GropName, MovieName):
        if GroupManager.hasObject(GropName, MovieName) is True:
            Movie = GroupManager.getObject(GropName, MovieName)
            with GuardBlockInput(source) as guard_source:
                with guard_source.addParallelTask(2) as (guard_source_movie, guard_source_fade):
                    guard_source_movie.addTask("TaskMovie2Play", Movie2=Movie, Wait=True, AutoEnable=True)

    def _onGenerate(self, source):
        source.addScope(self.SceneEffect, "Message", 'Movie2_Close')

        source.addTask("TaskInteractive", GroupName="Message", ObjectName="Socket_Block", Value=False)
        source.addTask("TaskSceneLayerGroupEnable", SceneName=self.SceneName, LayerName="Message", Value=False)
