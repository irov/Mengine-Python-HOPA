from Foundation.Entity.BaseEntity import BaseEntity

from Notification import Notification

Enigma = Mengine.importEntity("Enigma")

class ZoomAfterFrame(BaseEntity):
    def __init__(self):
        super(ZoomAfterFrame, self).__init__()
        pass

    def _onActivate(self):
        super(ZoomAfterFrame, self)._onActivate()
        Notification.notify(Notificator.onZoomAttachToFrame, self)
        pass

    def _onDeactivate(self):
        super(ZoomAfterFrame, self)._onDeactivate()
        Notification.notify(Notificator.onZoomDeAttachToFrame, self)
        pass

    pass