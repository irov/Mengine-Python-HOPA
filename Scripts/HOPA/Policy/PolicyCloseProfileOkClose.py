from Foundation.Task.TaskAlias import TaskAlias

class PolicyCloseProfileOkClose(TaskAlias):
    def _onParams(self, params):
        super(PolicyCloseProfileOkClose, self)._onParams(params)
        pass

    def _onGenerate(self, source):
        with source.addRaceTask(2) as (tc_ok, tc_close):
            tc_ok.addTask("TaskButtonClick", GroupName="Profile", ButtonName="Button_Ok")
            tc_close.addTask("TaskButtonClick", GroupName="Profile", ButtonName="Button_Close")
            pass
        pass
    pass