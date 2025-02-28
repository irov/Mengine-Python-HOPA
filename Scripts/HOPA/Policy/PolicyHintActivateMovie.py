from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintActivateMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintActivateMovie, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        # print "PolicyHintActivateMovie _onGenerate"
        SystemHint = SystemManager.getSystem("SystemHint")
        self.Hint = SystemHint.getHintObject()

        MovieGroup = self.Hint.getGroup()
        Movie_Activate = MovieGroup.getObject("Movie2_Activate")
        Movie2_Reload = MovieGroup.getObject("Movie2_Reload")

        source.addDisable(Movie2_Reload)

        source.addTask("TaskMovie2Play", Movie2=Movie_Activate, AutoEnable=True)
        pass

    pass
