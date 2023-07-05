from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasNotEnoughGold(TaskAlias):

    def _onParams(self, params):
        self.Gold = params.get("Gold")
        self.Descr = params.get("Descr")
        self.PageID = params.get("PageID")

    def _onGenerate(self, source):
        PolicyAction = PolicyManager.getPolicy("NotEnoughGoldAction")
        PolicySecondAction = PolicyManager.getPolicy("NotEnoughGoldSecondAction")

        if PolicyAction is not None:
            task = PolicyAction
        elif PolicySecondAction is not None:
            task = PolicySecondAction

        else:
            PolicyMessage = PolicyManager.getPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
            PolicyOnSkipAction = PolicyManager.getPolicy("NotEnoughGoldOnSkipAction")

            task = PolicyOnSkipAction or PolicyMessage

        source.addTask(task, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)
