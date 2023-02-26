"""
Created on 13.09.2011

@author: Me
"""

from Foundation.ArrowManager import ArrowManager
from Foundation.Entity.BaseEntity import BaseEntity
from Notification import Notification

class FanItem(BaseEntity):
    ITEM_NONE = 0
    ITEM_HAND = 1
    ITEM_FAN = 2

    def __init__(self):
        super(FanItem, self).__init__()
        self.state = FanItem.ITEM_NONE
        pass

    def _onActivate(self):
        Sprite_Item = self.object.getObject("Sprite_Item")
        Sprite_Item.setPosition((0, 0))

        self.setEventListener(onGlobalHandleMouseButtonEventEnd=self._onGlobalHandleMouseButtonEventEnd)
        pass

    def _onDeactivate(self):
        self.setEventListener(onGlobalHandleMouseButtonEventEnd=None)
        pass

    def inNone(self):
        self.state = FanItem.ITEM_NONE

        self.enableGlobalMouseEvent(False)
        pass

    def inHand(self):
        self.state = FanItem.ITEM_HAND

        self.enableGlobalMouseEvent(True)
        pass

    def inFan(self):
        self.state = FanItem.ITEM_FAN
        pass

    def _onGlobalHandleMouseButtonEventEnd(self, touchId, button, isDown):
        if button != 0 or isDown is False:
            return True
            pass

        if ArrowManager.emptyArrowAttach() is True:
            return True
            pass

        if self.state is not FanItem.ITEM_HAND:
            return True
            pass

        Notification.notify(Notificator.onFanItemInvalidUse, self.object)

        return True
        pass