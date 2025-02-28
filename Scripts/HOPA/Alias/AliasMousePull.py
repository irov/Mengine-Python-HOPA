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

    def _onGenerate(self, source):
        MovieObject = self.Group.getObject(self.MovieName)
        MovieWrongObject = self.Group.getObject(self.MovieWrongName)

        source.addDisable(MovieObject)
        source.addNotify(Notificator.onPullArrowAttach, self.Direction, MovieWrongObject, self.Object)  # place arrow

        source.addTask("TaskInteractive", Object=self.Object, Value=True)

        with source.addRepeatTask() as (tc_do, tc_until):
            if self.Object.getType() == "ObjectSocket":
                tc_do.addTask("TaskSocketClick", Socket=self.Object, AutoEnable=False)
            elif self.Object.getType() == "ObjectItem":
                tc_do.addTask("TaskItemClick", Item=self.Object, AutoEnable=False)

            with tc_do.addRaceTask(2) as (tc_bad_pull, tc_pull):
                tc_bad_pull.addListener(Notificator.onMousePull, Filter=self.acceptBadPull)  # on over clicking

                tc_pull.addTask("TaskMousePull", Direction=self.Direction, Distance=self.MinDistance)
                tc_pull.addNotify(Notificator.onPullWrong, MovieObject, MovieWrongObject)  # wrong pull

            tc_until.addListener(Notificator.onMousePull, Filter=self.acceptNicePull)
            tc_until.addTask("TaskInteractive", Object=self.Object, Value=False)

        source.addNotify(Notificator.onPullArrowDetach, self.Direction, self.Object)  # remove away arrow

        source.addEnable(MovieObject)
        source.addDisable(MovieWrongObject)

        source.addTask("TaskMoviePlay", Movie=MovieObject, Wait=True)
        source.addNotify(Notificator.onMousePullComplete)

    def acceptBadPull(self, direction, isBadPull):
        if direction != self.Direction:
            return False
        return not isBadPull

    def acceptNicePull(self, direction, isNicePull):
        if direction != self.Direction:
            return False
        return isNicePull
