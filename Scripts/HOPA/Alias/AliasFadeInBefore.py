from Foundation.ArrowManager import ArrowManager
from Foundation.DemonManager import DemonManager
from Foundation.PolicyManager import PolicyManager
from Foundation.Task.TaskAlias import TaskAlias


class AliasFadeInBefore(TaskAlias):
    def __init__(self):
        super(AliasFadeInBefore, self).__init__()
        pass

    def _onParams(self, params):
        super(AliasFadeInBefore, self)._onParams(params)
        pass

    def _onInitialize(self):
        super(AliasFadeInBefore, self)._onInitialize()
        pass

    def _onGenerate(self, source):
        if ArrowManager.emptyArrowAttach() is False:
            Inventory = DemonManager.getDemon("Inventory")
            PolicyReturnInventoryItem = PolicyManager.getPolicy("PolicyReturnInventoryItem",
                                                                "AliasInventoryReturnInventoryItem")
            source.addTask(PolicyReturnInventoryItem, Inventory=Inventory)
        else:
            source.addDummy()
