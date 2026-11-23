from Foundation.ArrowManager import ArrowManager
from Foundation.BaseEntity import BaseEntity

class FanItem(BaseEntity):
    ITEM_NONE = 0
    ITEM_HAND = 1
    ITEM_FAN = 2

    def __init__(self):
        super(FanItem, self).__init__()
        self.state = FanItem.ITEM_NONE
        self.MouseButtonHandlerID = 0
        pass

    def _onActivate(self):
        Sprite_Item = self.object.getObject("Sprite_Item")
        Sprite_Item.setPosition((0, 0))

        self.MouseButtonHandlerID = Mengine.addMouseButtonHandlerEnd(self._onGlobalHandleMouseButtonEventEnd, self.state == FanItem.ITEM_HAND)
        pass

    def _onDeactivate(self):
        if self.MouseButtonHandlerID != 0:
            Mengine.removeGlobalHandler(self.MouseButtonHandlerID)
            self.MouseButtonHandlerID = 0
        pass

    def inNone(self):
        self.state = FanItem.ITEM_NONE

        if self.MouseButtonHandlerID != 0:
            Mengine.enableGlobalHandler(self.MouseButtonHandlerID, False)
        pass

    def inHand(self):
        self.state = FanItem.ITEM_HAND

        if self.MouseButtonHandlerID != 0:
            Mengine.enableGlobalHandler(self.MouseButtonHandlerID, True)
        pass

    def inFan(self):
        self.state = FanItem.ITEM_FAN
        pass

    def _onGlobalHandleMouseButtonEventEnd(self, event):
        if event.button != 0 or event.isDown is False:
            return
            pass

        if ArrowManager.emptyArrowAttach() is True:
            return
            pass

        if self.state is not FanItem.ITEM_HAND:
            return
            pass

        Notification.notify(Notificator.onFanItemInvalidUse, self.object)

        return
        pass
