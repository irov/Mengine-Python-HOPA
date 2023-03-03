from Foundation.Task.Task import Task


class TaskHOGInventoryFoundItem(Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskHOGInventoryFoundItem, self)._onParams(params)

        self.HOGItemName = params.get("HOGItemName")
        self.HOGInventory = params.get("HOGInventory")
        pass

    def _onCheck(self):
        FoundItems = self.HOGInventory.getFoundItems()
        if self.HOGItemName in FoundItems:
            self.log("invalid run, item {!r} already found".format(self.HOGItemName))
            return False
            pass

        return True
        pass

    def _onRun(self):
        self.HOGInventory.appendParam("FoundItems", self.HOGItemName)
        return True
        pass

    pass
