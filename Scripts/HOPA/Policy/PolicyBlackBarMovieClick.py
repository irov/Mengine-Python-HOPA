from Foundation.Task.TaskAlias import TaskAlias

class PolicyBlackBarMovieClick(TaskAlias):
    def _onParams(self, params):
        super(PolicyBlackBarMovieClick, self)._onParams(params)

        self.TextID = params.get("TextID")
        self.Time = params.get("Time")
        pass

    def _onInitialize(self):
        super(PolicyBlackBarMovieClick, self)._onInitialize()

        self.Movie_Up = self.Group.getObject("Movie_Up")
        self.Movie_Down = self.Group.getObject("Movie_Down")
        self.Text_Message = self.Group.getObject("Text_Message")
        pass

    def _onGenerate(self, source):
        source.addTask("TaskEnable", Object=self.Text_Message)
        source.addTask("TaskTextSetTextID", Text=self.Text_Message, Value=self.TextID)

        source.addTask("TaskEnable", Object=self.Movie_Down, Value=True)
        source.addTask("TaskEnable", Object=self.Movie_Up, Value=False)

        TextEntityNode = self.Text_Message.getEntityNode()
        source.addTask("TaskMovieSlotAddChild", Movie=self.Movie_Down, SlotName="MindMessage", Node=TextEntityNode)

        source.addTask("TaskMoviePlay", Movie=self.Movie_Down, Wait=True)

        #        with source.addRaceTask(2) as (tc_click, tc_leave):
        #            tc_leave.addTask("TaskListener", ID = Notificator.onSceneDeactivate)
        #            tc_click.addTask("TaskSocketClick", SocketName = "Socket_Click")
        #            pass

        source.addTask("TaskDelay", Time=3 * 1000)  # speed fix

        source.addTask("TaskNodeRemoveFromParent", Node=TextEntityNode)
        source.addTask("TaskEnable", Object=self.Movie_Up, Value=True)
        source.addTask("TaskEnable", Object=self.Movie_Down, Value=False)
        source.addTask("TaskMovieSlotAddChild", Movie=self.Movie_Up, SlotName="MindMessage", Node=TextEntityNode)

        source.addTask("TaskMoviePlay", Movie=self.Movie_Up, Wait=True)

        source.addTask("TaskNodeRemoveFromParent", Node=TextEntityNode)
        source.addTask("TaskEnable", Object=self.Movie_Down, Value=False)

        source.addTask("TaskEnable", Object=self.Text_Message, Value=False)
        pass
    pass