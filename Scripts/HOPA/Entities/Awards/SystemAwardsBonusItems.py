from Foundation.System import System
from Foundation.TaskManager import TaskManager

from AwardsManager import AwardsManager

class SystemAwardsBonusItems(System):
    def _onParams(self, params):
        super(SystemAwardsBonusItems, self)._onParams(params)
        self.items = {}
        self.openAwards = []
        pass

    def _onSave(self):
        return (self.items, self.openAwards)
        pass

    def _onLoad(self, data_save):
        self.items, self.openAwards = data_save
        pass

    def _onRun(self):
        if len(self.items) == 0:
            self.items = AwardsManager.getBonusItems()
            pass

        for awardID, items in self.items.items():
            for item in items:
                if item in self.openAwards:
                    continue
                    pass

                with TaskManager.createTaskChain(Name="SystemAwardsBonusItems%s" % item.getName()) as tc:
                    tc.addTask("TaskItemClick", Item=item)
                    tc.addDisable(item)
                    tc.addFunction(self.__onBonusItemFound, awardID, item)
                    pass
                pass
            pass
        return True
        pass

    def _onStop(self):
        for awardID, items in self.items.items():
            for item in items:
                if TaskManager.existTaskChain("SystemAwardsBonusItems%s" % item.getName()):
                    TaskManager.cancelTaskChain("SystemAwardsBonusItems%s" % item.getName())
                    pass
                pass
            pass

        self.items = {}
        pass

    def __onBonusItemFound(self, awardID, item):
        if awardID not in self.items.keys():
            return False
            pass

        self.showAward(awardID, item)
        return False
        pass

    def showAward(self, awardID, item):
        if item in self.openAwards:
            return
            pass

        Notification.notify(Notificator.onAwardsOpen, awardID)
        self.openAwards.append(item)

        return False
        pass

    pass
