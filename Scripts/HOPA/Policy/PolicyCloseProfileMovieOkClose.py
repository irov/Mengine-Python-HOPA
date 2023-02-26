from Foundation.Task.TaskAlias import TaskAlias

class PolicyCloseProfileMovieOkClose(TaskAlias):
    def _onParams(self, params):
        super(PolicyCloseProfileMovieOkClose, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        with source.addRaceTask(2) as (tc_ok, tc_close):
            tc_ok.addTask("TaskMovie2ButtonClick", DemonName="Profile", Movie2ButtonName="Movie2Button_Profile_Ok")
            tc_close.addTask("TaskMovie2ButtonClick", DemonName="Profile", Movie2ButtonName="Movie2Button_Profile_Close")
            pass
        pass
    pass