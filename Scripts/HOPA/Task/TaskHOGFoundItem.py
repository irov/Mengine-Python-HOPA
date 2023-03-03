from Foundation.Task.Task import Task


class TaskHOGFoundItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskHOGFoundItem, self)._onParams(params)
        self.HOGItemName = params.get("HOGItemName")
        self.HOG = params.get("HOG")
        pass

    def _onCheck(self):
        FoundItems = self.HOG.getFoundItems()
        if self.HOGItemName in FoundItems:
            self.log("invalid run, item %s already found" % (self.HOGItemName,))
            return False
            pass

        return True
        pass

    def _onRun(self):
        self.HOG.appendParam("FoundItems", self.HOGItemName)

        return True
        pass

    pass
