from Foundation.Task.TaskAlias import TaskAlias


class PolicyCloseProfileOk(TaskAlias):

    def _onGenerate(self, source):
        source.addTask("TaskButtonClick", GroupName="Profile", ButtonName="Button_Ok")
