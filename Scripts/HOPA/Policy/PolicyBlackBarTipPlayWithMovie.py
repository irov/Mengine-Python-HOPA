from Foundation.Task.TaskAlias import TaskAlias

class PolicyBlackBarTipPlayWithMovie(TaskAlias):
    def _onParams(self, params):
        super(PolicyBlackBarTipPlayWithMovie, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.Time = params.get("Time")
        self.SkipStart = params.get("SkipStart", False)
        pass

    def _onGenerate(self, source):
        if self.Group.hasObject("Movie2_Mind") is True:
            self.MovieMind = self.Group.getObject("Movie2_Mind")
        elif self.Group.hasObject("Movie2_Mind") is True:
            self.MovieMind = self.Group.getObject("Movie_Mind")
        else:
            Trace.log("Task", 0, "There is no object %s or %s in group %s" % ("Movie2_Mind", "Movie_Mind", self.Group.getName()))

        moviePos = self.MovieMind.getPosition()
        viewport = Mengine.getGameViewport()
        newPosition = (moviePos[0], moviePos[1] + viewport.begin.y)

        source.addTask("TaskEnable", ObjectName="Text_Message")
        source.addTask("TaskObjectSetPosition", Object=self.MovieMind, Value=newPosition)
        source.addTask("TaskEnable", ObjectName=self.MovieMind.getName())

        source.addTask("TaskTextSetTextID", TextName="Text_Message", Value=self.TextID)
        source.addFunction(self.attachText, self.Group)

        # source.addTask("AliasObjectAlphaTo", Object=MovieMind, From=0.0, To=1.0, Time=1.0)

        source.addTask("TaskObjectSetAlpha", Object=self.MovieMind, Value=1.0)

        if self.SkipStart is True:
            source.addTask("TaskMovieLastFrame", Movie=self.MovieMind, Value=True)
        else:
            source.addTask("TaskMoviePlay", Movie=self.MovieMind, Wait=True)

        source.addTask("TaskDelay", Time=self.Time)

        source.addTask("AliasObjectAlphaTo", Object=self.MovieMind, From=1.0, To=0.0, Time=600.0)
        source.addFunction(self.deattachText, self.Group)
        source.addTask("TaskEnable", ObjectName="Text_Message", Value=False)
        source.addTask("TaskEnable", ObjectName=self.MovieMind.getName(), Value=False)
        source.addTask("TaskObjectSetPosition", Object=self.MovieMind, Value=moviePos)
        pass

    def attachText(self, Group):
        MovieEn = self.MovieMind.getEntity()

        NodeForText = MovieEn.getMovieSlot("MindMessage")
        self.MovieMind.setEnable(True)

        TextBox = Group.getObject("Text_Message")
        TextEntityNode = TextBox.getEntityNode()
        NodeForText.addChild(TextEntityNode)
        pass

    def deattachText(self, Group):
        TextBox = Group.getObject("Text_Message")
        TextEntity = TextBox.getEntity()
        TextEntity.removeFromParent()
        pass
    pass