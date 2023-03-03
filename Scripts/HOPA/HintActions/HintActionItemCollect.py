from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject

from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget
from HOPA.System.SystemItemCollect import SystemItemCollect

from Notification import Notification


class HintActionItemCollect(MixinObject, HintActionMultiTarget):

    def _onParams(self, params):
        super(HintActionItemCollect, self)._onParams(params)
        self.ItemList = params.get('ItemList')

    def _onCheck(self):
        Demon = DemonManager.getDemon('ItemCollect')
        if Demon.isActive() is False:
            return False

        if Demon.getEnable() is False:
            return False

        if SystemItemCollect.s_CurrentOpenItemCollect is None:
            return False

        if SystemItemCollect.s_CurrentOpenItemCollect != (self.SceneName, self.Object.getName()):
            return False

        return True

    def _onAction(self, _hint):
        self.NotificatorEnd = Notification.addObserver(Notificator.onHintActionItemCollectEnd, self.__onHintActionItemCollectEnd)
        self.getHintItem()

    def _getHintObject(self):
        return self.Object

    def __onHintActionItemCollectEnd(self):
        self._onEnd()

        return False

    def getHintItem(self):
        for itemName in self.ItemList:
            if SystemItemCollect.hasFoundItem(itemName):
                continue

            ItemCollect = SystemItemCollect.getItemCollect(itemName)

            self.showHint(ItemCollect.Item.calcWorldHintPoint(), ItemCollect.ItemPosition)
            break
