from Foundation.Task.Task import Task

class TaskHOGRollingComplete(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskHOGRollingComplete, self)._onParams(params)
        self.HOG = params.get("HOG")
        pass

    def _onRun(self):
        HogEntity = self.HOG.getEntity()
        HogEntity.checkComplete()

        return True
        pass

    pass