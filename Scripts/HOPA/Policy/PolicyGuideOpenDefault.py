from Foundation.Task.TaskAlias import TaskAlias

class PolicyGuideOpenDefault(TaskAlias):

    def _onParams(self, params):
        super(PolicyGuideOpenDefault, self)._onParams(params)
        self.ButtonName = params.get("Movie2ButtonName", "Movie2Button_Guide")

    def _onGenerate(self, source):
        source.addTask('TaskMovie2ButtonClick', GroupName=self.GroupName, Movie2ButtonName=self.ButtonName)
        source.addNotify(Notificator.onBonusSceneTransition, "Guide")