from Foundation.Task.TaskAlias import TaskAlias


class PolicyBlackBarPlayText(TaskAlias):
    def _onParams(self, params):
        super(PolicyBlackBarPlayText, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.Time = params.get("Time")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskTextSetTextID", TextName="Text_Message", Value=self.TextID)
        source.addTask("TaskEnable", ObjectName="Text_Message", Value=True)

        source.addDelay(self.Time)

        source.addTask("TaskEnable", ObjectName="Text_Message", Value=False)
        pass

    pass
