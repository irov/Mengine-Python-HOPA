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
        source.addEnable(self.Text_Message)
        source.addTask("TaskTextSetTextID", Text=self.Text_Message, Value=self.TextID)

        source.addEnable(self.Movie_Down)
        source.addDisable(self.Movie_Up)

        TextEntityNode = self.Text_Message.getEntityNode()
        source.addTask("TaskMovieSlotAddChild", Movie=self.Movie_Down, SlotName="MindMessage", Node=TextEntityNode)

        source.addTask("TaskMoviePlay", Movie=self.Movie_Down, Wait=True)

        #        with source.addRaceTask(2) as (tc_click, tc_leave):
        #            tc_leave.addListener(Notificator.onSceneDeactivate)
        #            tc_click.addTask("TaskSocketClick", SocketName = "Socket_Click")
        #            pass

        source.addDelay(3 * 1000)  # speed fix

        source.addTask("TaskNodeRemoveFromParent", Node=TextEntityNode)
        source.addEnable(self.Movie_Up)
        source.addDisable(self.Movie_Down)
        source.addTask("TaskMovieSlotAddChild", Movie=self.Movie_Up, SlotName="MindMessage", Node=TextEntityNode)

        source.addTask("TaskMoviePlay", Movie=self.Movie_Up, Wait=True)

        source.addTask("TaskNodeRemoveFromParent", Node=TextEntityNode)
        source.addDisable(self.Movie_Down)
        source.addDisable(self.Text_Message)
        pass

    pass
