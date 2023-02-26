from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyHintReloadMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReloadMovie, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        SystemHint = SystemManager.getSystem("SystemHint")
        self.Hint = SystemHint.getHintObject()

        MovieGroup = self.Hint.getGroup()
        Movie2_Reload = MovieGroup.getObject("Movie2_Reload")
        Movie2_Reload.setEnable(True)
        Movie_ReloadDuration = Movie2_Reload.getDuration()
        SystemHint = SystemManager.getSystem("SystemHint")
        CurrentReloadTiming = SystemHint.getCurrentTiming()

        if Movie_ReloadDuration == CurrentReloadTiming:
            if SystemHint.isReloadStarted() is False:
                Movie2_Reload.setLastFrame(True)
                return
                pass
            CurrentReloadTiming = 0
            pass

        if MovieGroup.hasObject("Movie2_Ready"):
            Movie_Ready = MovieGroup.getObject("Movie2_Ready")
            Movie_Ready.setEnable(False)
            pass
        if MovieGroup.hasObject("Movie2_Ready_Effect"):
            Movie_Ready = MovieGroup.getObject("Movie2_Ready_Effect")
            Movie_Ready.setEnable(False)
            pass
        source.addTask("TaskMovie2Play", Movie2=Movie2_Reload, StartTiming=CurrentReloadTiming, Wait=True, LastFrame=None)
        source.addParam(Movie2_Reload, "StartTiming", None)
        pass