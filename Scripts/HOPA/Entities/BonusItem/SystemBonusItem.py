from Foundation.DemonManager import DemonManager
from Foundation.GroupManager import GroupManager
from Foundation.System import System
from Foundation.TaskManager import TaskManager
from HOPA.BonusItemManager import BonusItemManager


class SystemBonusItem(System):
    def _onParams(self, params):
        super(SystemBonusItem, self)._onParams(params)
        self._currentCount = 0
        self.bonusList = []

    def _onSave(self):
        return self.BonusInventory.getItemsCount()
        pass

    def _onLoad(self, data_save):
        self._currentCount = data_save
        pass

    def _onRun(self):
        BonusItem = DemonManager.getDemon("BonusItem")
        self.BonusInventory = BonusItem.getEntity()
        self.BonusInventory.setItemsCount(self._currentCount)

        self.addObserver(Notificator.onSceneEnter, self.__onSceneEnter)
        self.addObserver(Notificator.onSceneLeave, self.__onSceneLeave)
        pass

    def _onStop(self):
        self.__cleanBonusList()
        pass

    def __onSceneEnter(self, sceneName):
        self.bonusList = BonusItemManager.hasBonusItem(sceneName)

        for group in self.bonusList:
            for item in self.bonusList[group]:
                ItemObject = GroupManager.getObject(group, item)

                with TaskManager.createTaskChain(Name="BonusItemTaskChain_%s_%s" % (group, item,)) as tc:
                    tc.addTask("TaskItemClick", Item=ItemObject)
                    tc.addTask("TaskItemPick", Item=ItemObject)
                    tc.addFunction(self.BonusInventory._updateCount)

        return False

    def __cleanBonusList(self):
        for group in self.bonusList:
            for item in self.bonusList[group]:
                if TaskManager.existTaskChain("BonusItemTaskChain_%s_%s" % (group, item,)):
                    TaskManager.cancelTaskChain("BonusItemTaskChain_%s_%s" % (group, item,))

        self.bonusList = []

    def __onSceneLeave(self, sceneName):
        self.__cleanBonusList()
        return False
