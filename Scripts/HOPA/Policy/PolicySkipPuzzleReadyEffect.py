from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


ALPHA_OUT_TIME = 2500.0


class PolicySkipPuzzleReadyEffect(TaskAlias):
    def _onParams(self, params):
        super(PolicySkipPuzzleReadyEffect, self)._onParams(params)
        self.SkipPuzzle = DemonManager.getDemon("SkipPuzzle")

    def _onGenerate(self, source):
        # = old logic ==================================================================================
        # if self.SkipPuzzle.hasObject("Movie2_Ready") is True:
        #
        #     Movie_Ready = self.SkipPuzzle.getObject("Movie2_Ready")
        #
        #     Particles2=None
        #
        #     print "Find me and Fix plz"
        #     print "_____Blocker with shadows"
        #     Movie_Ready.appendParam("DisableLayers", "Particles2")     #and here ARHANOID
        #
        #     source.addTask("TaskEnable",  Object = Movie_Ready)
        #     with source.addParallelTask(2) as (tc_alpha, tc_play):
        #         if Particles2 != None:
        #             tc_alpha.addTask("TaskNodeAlphaTo", Node=Particles2, From=0.0, To=1.0, Time=1000)
        #             tc_alpha.addTask("TaskNodeAlphaTo", Node=Particles2, From=1.0, To=0.0, Time=0.001)
        #         tc_play.addTask("TaskMovie2Play",  Movie2=Movie_Ready, Loop = True, Wait = False)

        #     source.addFunction(Movie_Ready.delParam, "DisableLayers", "Particles2")  #here ARHANOID
        # = new logic ==================================================================================
        if self.SkipPuzzle.hasObject("Movie2_Ready_Effect"):
            MovieReady_Effect = self.SkipPuzzle.getObject("Movie2_Ready_Effect")

            source.addEnable(MovieReady_Effect)
            with source.addFork() as source_fork:
                with source_fork.addParallelTask(2) as (source_alpha, source_play):
                    source_alpha.addTask("AliasObjectAlphaTo", Object=MovieReady_Effect,
                                         Time=ALPHA_OUT_TIME, From=0.0, To=1.0)
                    source_play.addTask("TaskMovie2Play", Movie2=MovieReady_Effect, Loop=True, Wait=False)

        if self.SkipPuzzle.hasObject("Movie2_Ready") is True:
            Movie_Ready = self.SkipPuzzle.getObject("Movie2_Ready")

            source.addEnable(Movie_Ready)
            source.addTask("TaskMovie2Play", Movie2=Movie_Ready, Loop=True, Wait=False)
        # ==============================================================================================

        PolicySkipPuzzleClick = PolicyManager.getPolicy("SkipPuzzleClick", "PolicySkipPuzzleClickButton")

        with source.addRaceTask(2) as (tc_click, tc_skip):
            # tc_click.addTask("TaskButtonClick", ButtonName = "Button_Skip")
            tc_click.addTask(PolicySkipPuzzleClick)
            tc_skip.addListener(Notificator.onEnigmaSkip)

        if self.SkipPuzzle.hasObject("Movie2_Ready") is True:
            Movie_Ready = self.SkipPuzzle.getObject("Movie2_Ready")

            source.addTask("TaskMovie2Stop", Movie2=Movie_Ready)

