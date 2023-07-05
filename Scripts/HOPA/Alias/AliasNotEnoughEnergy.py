from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasNotEnoughEnergy(TaskAlias):

    def _onParams(self, params):
        self.Action = params.get("Action")
        self.PageID = params.get("PageID")

    def _onGenerate(self, source):
        PolicyMessage = PolicyManager.getPolicy("NotEnoughEnergyMessage", "PolicyNotEnoughEnergyDialog")
        PolicyAction = PolicyManager.getPolicy("NotEnoughEnergyAction")
        PolicySecondAction = PolicyManager.getPolicy("NotEnoughEnergySecondAction")

        if PolicyAction is not None:
            source.addTask(PolicyAction, Action=self.Action, PageID=self.PageID)
        else:
            if PolicySecondAction is not None:
                source.addTask(PolicySecondAction, Action=self.Action, PageID=self.PageID)
            else:
                source.addTask(PolicyMessage, Action=self.Action, PageID=self.PageID)
