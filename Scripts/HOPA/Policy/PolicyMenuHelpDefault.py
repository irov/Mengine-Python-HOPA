from Foundation.Task.TaskAlias import TaskAlias

class PolicyMenuHelpDefault(TaskAlias):

    def _onGenerate(self, source):
        source.addTask("TaskButtonClick", GroupName="Menu_Background", ButtonName="Button_Help")
        with source.addRaceTask(2) as (tc_help, tc_leave):
            tc_help.addTask("TaskSceneLayerGroupEnable", LayerName="MenuHelp", Value=True)
            tc_help.addTask("AliasFadeIn", FadeGroupName="Fade", To=0.5, Time=0.25 * 1000)  # speed fix

            tc_help.addTask("TaskButtonClick", DemonName="MenuHelp", ButtonName="Button_Ok")
            tc_help.addTask("TaskSceneLayerGroupEnable", LayerName="MenuHelp", Value=False)
            tc_help.addTask("AliasFadeOut", FadeGroupName="Fade", Time=0.25, From=0.7)

            tc_leave.addTask("TaskSceneLeave", SceneAny=True)
            pass
        pass
    pass