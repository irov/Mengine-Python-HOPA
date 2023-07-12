from Foundation.Task.TaskAlias import TaskAlias


class TaskHOGFindItemClick(TaskAlias):
    def _onParams(self, params):
        super(TaskHOGFindItemClick, self)._onParams(params)
        self.HOGItem = params.get("HOGItem")
        self.ItemObject = params.get("ItemObject")

    def _scopeClick(self, source):
        ObjectType = self.ItemObject.getType()

        if ObjectType in ["ObjectMovieItem", "ObjectMovie2Item"]:
            source.addTask("TaskMovieItemClick", MovieItem=self.ItemObject)
        else:
            ItemName = self.HOGItem.objectName
            source.addTask("TaskItemClick", ItemName=ItemName)

    def _onGenerate(self, source):
        done_event = Event("onHOGFindItemClickEnergyDone")

        with source.addRepeatTask() as (repeat, until):
            repeat.addScope(self._scopeClick)
            repeat.addTask("AliasEnergyConsume", Action="FindHO", Cb=done_event)

            until.addEvent(done_event)

