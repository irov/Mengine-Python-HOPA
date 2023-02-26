from Foundation.Task.MixinGroup import MixinGroup
from Foundation.Task.MixinObserver import MixinObserver
from Foundation.Task.Task import Task

class TaskItemPopUp(MixinGroup, MixinObserver, Task):
    Skiped = True

    def _onParams(self, params):
        super(TaskItemPopUp, self)._onParams(params)

        self.ItemName = params.get("ItemName")
        pass

    def _onInitialize(self):
        super(TaskItemPopUp, self)._onInitialize()
        pass

    def _onRun(self):
        Demon_ItemPopUp = self.Group.getObject("Demon_ItemPopUp")

        Demon_ItemPopUp.setParam("ItemName", self.ItemName)
        Demon_ItemPopUp.setParam("Open", True)

        self.addObserverFilter(Notificator.onItemPopUpClose, self.__onItemPopUpCloseFilter, self.ItemName)

        return False
        pass

    def __onItemPopUpCloseFilter(self, name):
        return True
        pass

    pass