from Foundation.Task.TaskAlias import TaskAlias

class AliasBombGameBombRotate(TaskAlias):
    def __init__(self):
        super(AliasBombGameBombRotate, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasBombGameBombRotate, self)._onParams(params)
        self.Bomb = params.get("Bomb")
        self.Movie = [None]
        self.DelayEnd = [0]  # for exit from repite loop for procces notify listener
        pass

    def _onInitialize(self):
        super(AliasBombGameBombRotate, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        bomb = self.Bomb[0]
        if (bomb.HaveMoveDir() is False):
            return
            pass

        def mov():
            res = bomb.Move()
            bomb.getMovie(self.Movie)
            pass

        def TryEndMovBef():
            if (len(self.Movie[0]) == 0 or self.Movie[0][0] is None):
                self.DelayEnd[0] = 0.1
                self.DelayEnd[0] *= 1000  # speed fix
                Notification.notify(Notificator.onBombEndMov, self.Bomb)
                pass

            pass

        def movEnd():
            bomb.EndMove()
            pass

        def TryEndMovAft():
            if (bomb.Result == bomb.Move_Exploud or bomb.Result == bomb.Move_Out):
                self.DelayEnd[0] = 0.1
                self.DelayEnd[0] *= 1000  # speed fix
                Notification.notify(Notificator.onBombEndMov, self.Bomb)
                pass
            pass

        def Filter(Bomb):
            if (Bomb == self.Bomb):
                return True
            return False

        pass

        with source.addRepeatTask() as (tc_do, tc_until):
            tc_do.addFunction(mov)
            tc_do.addFunction(TryEndMovBef)
            tc_do.addTask("TaskDelayPointer", TimePointer=self.DelayEnd)
            tc_do.addTask("AliasMultyplMovePlay", Movies=self.Movie)

            tc_do.addFunction(movEnd)
            tc_do.addFunction(TryEndMovAft)
            tc_do.addTask("TaskDelayPointer", TimePointer=self.DelayEnd)

            tc_until.addListener(Notificator.onBombEndMov, Filter=Filter)
        pass

    pass
