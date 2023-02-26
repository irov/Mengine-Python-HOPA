from Foundation.Task.MixinObject import MixinObject
from Foundation.Task.TaskAlias import TaskAlias

class AliasMousePull(MixinObject, TaskAlias):
    s_directions = ["Up", 'UpRight', 'Right', "DownRight", "Down", "DownLeft", "Left", "UpLeft"]
    s_angle = [i * 360 / len(s_directions) for i in range(len(s_directions))]

    def _onParams(self, params):
        super(AliasMousePull, self)._onParams(params)
        self.MovieName = params.get("MovieName")
        self.MovieWrongName = params.get("MovieWrongName")
        self.Direction = params.get("Direction")
        self.MinDistance = params.get("Distance")
        pass

    def _onInitialize(self):
        super(AliasMousePull, self)._onInitialize()

        if _DEVELOPMENT is True:
            if self.Direction not in AliasMousePull.s_directions:
                self.initializeFailed("AliasMousePull invalid Direction %s" % (self.Direction,))
                pass
            pass
        pass

    def _onGenerate(self, source):
        MovieObject = self.Group.getObject(self.MovieName)
        MovieWrongObject = self.Group.getObject(self.MovieWrongName)

        source.addTask("TaskEnable", Object=MovieObject, Value=False)
        source.addTask("TaskNotify", ID=Notificator.onPullArrowAttach, Args=(self.Direction, MovieWrongObject, self.Object))  # place arrow

        source.addTask("TaskInteractive", Object=self.Object, Value=True)

        with source.addRepeatTask() as (tc_do, tc_until):
            if self.Object.getType() == "ObjectSocket":
                tc_do.addTask("TaskSocketClick", Socket=self.Object, AutoEnable=False)
                pass
            elif self.Object.getType() == "ObjectItem":
                tc_do.addTask("TaskItemClick", Item=self.Object, AutoEnable=False)
                pass

            with tc_do.addRaceTask(2) as (tc_bad_pull, tc_pull):
                tc_bad_pull.addTask("TaskListener", ID=Notificator.onMousePull, Filter=self.acceptBadPull)  # on over clicking

                tc_pull.addTask("TaskMousePull", Direction=self.Direction, Distance=self.MinDistance)
                tc_pull.addTask("TaskNotify", ID=Notificator.onPullWrong, Args=(MovieObject, MovieWrongObject))  # wrong pull
                pass

            tc_until.addTask("TaskListener", ID=Notificator.onMousePull, Filter=self.acceptNicePull)
            tc_until.addTask("TaskInteractive", Object=self.Object, Value=False)
            pass

        source.addTask("TaskNotify", ID=Notificator.onPullArrowDetach, Args=(self.Direction, self.Object))  # remove away arrow

        source.addTask("TaskEnable", Object=MovieObject, Value=True)
        source.addTask("TaskEnable", Object=MovieWrongObject, Value=False)

        source.addTask("TaskMoviePlay", Movie=MovieObject, Wait=True)
        source.addTask("TaskNotify", ID=Notificator.onMousePullComplete)
        pass

    def acceptBadPull(self, direction, isBadPull):
        if direction != self.Direction:
            return False
            pass
        return not isBadPull
        pass

    def acceptNicePull(self, direction, isNicePull):
        if direction != self.Direction:
            return False
            pass
        return isNicePull
        pass

    pass