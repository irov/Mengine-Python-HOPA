from Foundation.Entity.BaseEntity import BaseEntity

from StrategyGuidePageManager import StrategyGuidePageManager

class StrategyGuidePage(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def __init__(self):
        super(StrategyGuidePage, self).__init__()
        self.sockets = []
        pass

    def _onPreparation(self):
        super(StrategyGuidePage, self)._onPreparation()
        self.sockets = StrategyGuidePageManager.getSockets(self.object)

        for socket in self.sockets:
            socket.setInteractive(True)
            pass
        pass

    def _onActivate(self):
        super(StrategyGuidePage, self)._onActivate()
        pass

    def _onDeactivate(self):
        super(StrategyGuidePage, self)._onDeactivate()
        for socket in self.sockets:
            socket.setInteractive(False)
            pass

        self.sockets = []
        pass

    pass