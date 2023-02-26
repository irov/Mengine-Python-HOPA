from Foundation.Entity.BaseEntity import BaseEntity
from Notification import Notification

from StrategyGuideZoomManager import StrategyGuideZoomManager

class StrategyGuideZoom(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def __init__(self):
        super(StrategyGuideZoom, self).__init__()
        self.zooms = {}
        self.currenZoom = None
        self.socketClose = None
        self.SocketClickObserver = None

        pass

    def _onPreparation(self):
        super(StrategyGuideZoom, self)._onPreparation()

        self.socketClose = self.object.getObject("Socket_CloseZoom")
        self.socketClose.setEnable(False)

        self.zooms = StrategyGuideZoomManager.getZooms()

        self.SocketClickObserver = Notification.addObserver(Notificator.onSocketClick, self.__onOpenGuideZoom)
        pass

    def __onOpenGuideZoom(self, socket):
        if socket in self.zooms.keys():
            self.currenZoom = self.zooms[socket]
            self.currenZoom.setEnable(True)
            self.socketClose.setEnable(True)
            return False
            pass
        if socket is self.socketClose:
            self.currenZoom.setEnable(False)
            self.socketClose.setEnable(False)
            self.currenZoom = None
            return False
            pass
        return False
        pass

    def _onActivate(self):
        super(StrategyGuideZoom, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(StrategyGuideZoom, self)._onDeactivate()
        Notification.removeObserver(self.SocketClickObserver)
        self.SocketClickObserver = None
        if self.currenZoom is not None:
            self.currenZoom.setEnable(False)
            self.currenZoom = None
            self.socketClose.setEnable(False)
            self.socketClose = None
            pass
        pass

    pass