from Foundation.Task.TaskAlias import TaskAlias


class PolicyBlackBarPlayStatic(TaskAlias):
    def _onParams(self, params):
        super(PolicyBlackBarPlayStatic, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.Time = params.get("Time")
        self.Static = params.get("Static")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskTextSetTextID", TextName="Text_Message", Value=self.TextID)

        if self.Group.hasObject("Sprite_BlackBar") is True:
            source.addTask("TaskEnable", ObjectName="Sprite_BlackBar")
            source.addTask("AliasObjectAlphaTo", ObjectName="Sprite_BlackBar", Time=0.1 * 1000, From=0.0, To=1.0)
            pass

        source.addTask("TaskEnable", ObjectName="Text_Message")
        with source.addIfTask(lambda: self.Static is True) as (true, false):
            true.addListener(Notificator.onZoomClose)
            false.addTask("TaskDelay", Time=self.Time)

        if self.Group.hasObject("Sprite_BlackBar") is True:
            source.addTask("AliasObjectAlphaTo", ObjectName="Sprite_BlackBar", Time=0.1 * 1000, To=0.0)  # speed fix
            source.addTask("TaskEnable", ObjectName="Sprite_BlackBar", Value=False)
            pass

        source.addTask("TaskEnable", ObjectName="Text_Message", Value=False)
