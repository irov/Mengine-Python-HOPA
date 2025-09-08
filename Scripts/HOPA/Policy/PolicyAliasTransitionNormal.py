from Foundation.Task.TaskAlias import TaskAlias


class PolicyAliasTransitionNormal(TaskAlias):
    def _onParams(self, params):
        super(PolicyAliasTransitionNormal, self)._onParams(params)
        self.SceneName=params.get("SceneName")
        self.Wait=params.get("Wait")
        self.SkipTaskChains=params.get("SkipTaskChains")
        self.CheckToScene=params.get("CheckToScene", True)
        pass

    def _onGenerate(self, source):
        source.addTask("TaskTransition", SceneName=self.SceneName, Wait=self.Wait, SkipTaskChains=self.SkipTaskChains, CheckToScene=self.CheckToScene)
        pass

    pass
