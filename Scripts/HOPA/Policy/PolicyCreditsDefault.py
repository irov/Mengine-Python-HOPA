from Foundation.Task.TaskAlias import TaskAlias


class PolicyCreditsDefault(TaskAlias):
    def _onGenerate(self, source):
        SceneNameTo = "Credits"
        source.addTask("AliasTransition", SceneName=SceneNameTo)

        # source.addTask("TaskMovieButtonClick", GroupName="Menu_Background", ButtonName="MovieButton_Credits")
        # with source.addRaceTask(2) as (tc_credits, tc_leave):
        #
        # tc_credits.addTask("TaskSceneLayerGroupEnable", LayerName="Credits", Value=True)
        #
        # tc_credits.addTask("TaskSceneLayerGroupEnable", LayerName="CreditsBack", Value=True)
        #
        # with tc_credits.addRaceTask(3) as (tc_1, tc_2, tc_Movie):
        #     if GroupManager.hasObject("Menu_Background", "Movie2Button_Credits"):
        #         tc_1.addTask("TaskMovie2ButtonClick", GroupName="Menu_Background", Movie2ButtonName="Movie2Button_Credits")
        #
        #     elif GroupManager.hasObject("Menu_Background", "MovieButton_Credits"):
        #         tc_1.addTask("TaskMovieButtonClick", GroupName="Menu_Background", MovieButtonName="MovieButton_Credits")
        #
        #         tc_2.addTask("TaskButtonClick", GroupName="Credits", ButtonName="Button_OK")
        #
        #         tc_Movie.addTask("TaskMovie2Play", GroupName="Credits", Movie2Name="Movie2_Credits", Wait=True)
        #
        # tc_credits.addListener(Notificator.onCreditsEnd)
        #
        # tc_credits.addTask("TaskSceneLayerGroupEnable", LayerName="CreditsBack", Value=False)
        # tc_credits.addTask("TaskSceneLayerGroupEnable", LayerName="Credits", Value=False)
        #
        # tc_leave.addTask("TaskSceneLeave", SceneAny=True)
