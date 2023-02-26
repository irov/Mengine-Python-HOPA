from Foundation.SystemManager import SystemManager
from Foundation.Task.TaskAlias import TaskAlias

class PolicyEnergyClickItem(TaskAlias):

    def _onParams(self, params):
        self.Item = params.get("Item")

    def _onInitialize(self):
        if self.Item is None:
            self.initializeFailed("PolicyEnergyClickItem should takes Item or MovieItem as param")

    def _scopeClickItem(self, source):
        source.addTask("TaskItemClick", Item=self.Item)

    def _onGenerate(self, source):
        SystemEnergy = SystemManager.getSystem("SystemEnergy")

        with source.addRepeatTask() as (repeat, until):
            repeat.addScope(self._scopeClickItem)
            repeat.addDelay(1.0)

            until.addScope(self._scopeClickItem)
            with until.addIfTask(SystemEnergy.consume, "PickItem") as (true, false):
                false.addBlock()