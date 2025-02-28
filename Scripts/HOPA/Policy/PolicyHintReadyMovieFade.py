from Foundation.GroupManager import GroupManager
from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias


class PolicyHintReadyMovieFade(TaskAlias):
    def _onParams(self, params):
        super(PolicyHintReadyMovieFade, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        LayerGroup = GroupManager.getGroup("Hint")
        active = LayerGroup.getEnable()

        if active is False:
            return

        SystemHint = SystemManager.getSystem("SystemHint")
        self.Hint = SystemHint.getHintObject()

        MovieGroup = self.Hint.getGroup()
        MovieReady = MovieGroup.getObject("Movie2_Ready")
        Movie_Reload = MovieGroup.getObject("Movie2_Reload")

        source.addDisable(Movie_Reload)
        source.addEnable(MovieReady)
        with source.addParallelTask(2) as (tc_Play, tc_Effect):
            if MovieGroup.hasObject("Movie2_Ready_Effect"):
                MovieReady_Effect = MovieGroup.getObject("Movie2_Ready_Effect")
                tc_Effect.addEnable(MovieReady_Effect)

                with tc_Effect.addFork() as source_fork:
                    with source_fork.addParallelTask(2) as (tc_Movie, Tc_Alpha):
                        Tc_Alpha.addTask("AliasObjectAlphaTo", Object=MovieReady_Effect, Time=2500.0, From=0.0, To=1.0)
                        tc_Movie.addTask("TaskMovie2Play", Movie2=MovieReady_Effect, Loop=True, Wait=False)

            tc_Play.addTask("TaskMovie2Play", Movie2=MovieReady, Loop=True, Wait=False)
        pass

    pass
