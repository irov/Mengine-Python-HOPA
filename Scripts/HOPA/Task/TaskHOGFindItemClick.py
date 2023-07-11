from Foundation.SystemManager import SystemManager
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
        if SystemManager.hasSystem("SystemEnergy") is False:
            source.addScope(self._scopeClick)
            return

        SystemEnergy = SystemManager.getSystem("SystemEnergy")
        done_event = Event("HOGFindItemClickEnergyDone")

        with source.addRepeatTask() as (repeat, until):
            repeat.addScope(self._scopeClick)
            with repeat.addIfTask(SystemEnergy.performAction, "FindHO") as (true, false):
                true.addFunction(done_event)

            until.addEvent(done_event)

