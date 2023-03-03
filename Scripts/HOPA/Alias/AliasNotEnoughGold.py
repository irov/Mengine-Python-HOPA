from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasNotEnoughGold(TaskAlias):

    def _onParams(self, params):
        self.Gold = params.get("Gold")
        self.Descr = params.get("Descr")
        self.PageID = params.get("PageID")

    def _onGenerate(self, source):
        PolicyMessage = PolicyManager.getPolicy("NotEnoughGoldMessage", "PolicyNotEnoughGoldDialog")
        PolicyAction = PolicyManager.getPolicy("NotEnoughGoldAction")

        if PolicyAction is not None:
            source.addTask(PolicyAction, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)
        else:
            source.addTask(PolicyMessage, Gold=self.Gold, Descr=self.Descr, PageID=self.PageID)
