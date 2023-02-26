from Foundation.Task.TaskAlias import TaskAlias

class PolicyBlackBarPlayWithMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyBlackBarPlayWithMovie, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.Time = params.get("Time")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskEnable", ObjectName="Text_Message")
        source.addTask("TaskObjectSetPosition", Object=self.MovieMind, Value=newPosition)
        source.addTask("TaskEnable", ObjectName="Movie2_Mind")
        source.addTask("TaskFunction", Fn=self.attachText)
        source.addTask("TaskTextSetTextID", TextName="Text_Message", Value=self.TextID)

        source.addTask("TaskMoviePlay", Movie=self.MovieMind)
        source.addTask("TaskDelay", Time=self.Time)
        source.addTask("TaskFunction", Fn=self.deattachText)
        source.addTask("TaskEnable", ObjectName="Text_Message", Value=False)
        source.addTask("TaskEnable", ObjectName="Movie2_Mind", Value=False)
        source.addTask("TaskObjectSetPosition", Object=self.MovieMind, Value=moviePos)
        pass
    pass

    def attachText(self):
        TextBox = self.Group.getObject("Text_Message")
        self.TextEntity = TextBox.getEntity()
        MovieEn = self.MovieMind.getEntity()
        self.NodeForText = MovieEn.getMovieSlot("MindMessage")
        self.MovieMind.setEnable(True)
        self.NodeForText.addChild(self.TextEntity)
        return

    def deattachText(self):
        self.TextEntity.removeFromParent()
        return