from Foundation.Task.Task import Task

class TaskHOGComplete(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskHOGComplete, self)._onParams(params)
        self.HOG = params.get("HOG")

        pass

    def _onRun(self):
        HOGItems = self.HOG.getHOGItems()
        HOGFoundItems = self.HOG.getFoundItems()

        if len(HOGItems) == len(HOGFoundItems):
            self.HOG.setComplete(True)
            pass

        return True
        pass

    pass