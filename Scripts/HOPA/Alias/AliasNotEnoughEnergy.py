from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasNotEnoughEnergy(TaskAlias):

    def _onParams(self, params):
        self.Action = params.get("Action")
        self.PageID = params.get("PageID")
        self.Amount = params.get("Amount")

    def _onGenerate(self, source):
        PolicyAction = PolicyManager.getPolicy("NotEnoughEnergyAction")
        PolicySecondAction = PolicyManager.getPolicy("NotEnoughEnergySecondAction")

        if PolicyAction is not None:
            task = PolicyAction
        elif PolicySecondAction is not None:
            task = PolicySecondAction

        else:
            PolicyMessage = PolicyManager.getPolicy("NotEnoughEnergyMessage", "PolicyNotEnoughEnergyDialog")
            PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughEnergyOnSkipAction")

            task = PolicyOnSkipAction or PolicyMessage

        source.addTask(task, Action=self.Action, PageID=self.Amount, Amount=self.Amount)
