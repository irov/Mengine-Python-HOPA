from Foundation.DemonManager import DemonManager
from Foundation.Notificator import Notificator
from Foundation.Task.MixinObject import MixinObject

from HOPA.HintActions.HintActionMultiTarget import HintActionMultiTarget
from HOPA.System.SystemItemCollect import SystemItemCollect

from Notification import Notification


class HintActionItemCollect(MixinObject, HintActionMultiTarget):

    def __init__(self):
        super(HintActionItemCollect, self).__init__()
        self.NotificatorEnd = None

    def __removeEndObserver(self):
        if self.NotificatorEnd is None:
            return

        Notification.removeObserver(self.NotificatorEnd)
        self.NotificatorEnd = None

    def _onEnd(self, someargs=None):
        # Detach before the base can notify that the hint has ended.
        self.__removeEndObserver()
        super(HintActionItemCollect, self)._onEnd(someargs)

    def _onFinalize(self):
        super(HintActionItemCollect, self)._onFinalize()

        self.__removeEndObserver()

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

    def _onAction(self, source, _hint):
        self.__removeEndObserver()
        self.NotificatorEnd = Notification.addObserver(Notificator.onHintActionItemCollectEnd, self.__onHintActionItemCollectEnd)
        self.getHintItem(source)

    def _getHintObject(self):
        return self.Object

    def __onHintActionItemCollectEnd(self):
        self._onEnd()

        return False

    def getHintItem(self, source):
        for itemName in self.ItemList:
            if SystemItemCollect.hasFoundItem(itemName):
                continue

            ItemCollect = SystemItemCollect.getItemCollect(itemName)

            self.showHint(source, ItemCollect.Item.calcWorldHintPoint(), ItemCollect.ItemPosition)
            break
