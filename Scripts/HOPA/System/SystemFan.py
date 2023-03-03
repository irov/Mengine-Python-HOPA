from Foundation.Notificator import Notificator
from Foundation.System import System


class SystemFan(System):
    def __init__(self):
        super(SystemFan, self).__init__()
        self.fans = {}
        self.OpenObserver = None
        self.CloseObserver = None
        self.onTtansition = None
        self.CurrentFan = None
        self.calledFan = None
        self.disableOpen = False
        self.FanCloseDone = None
        self.TransFan = None
        pass

    def _onRun(self):
        self.addObserver(Notificator.onFanOpen, self.__openFan)
        self.addObserver(Notificator.onFanClose, self.__closeFan)
        self.addObserver(Notificator.onFanCloseDone, self._removeCurrentFan)
        pass

    def _onStop(self):
        pass

    def _onInitialize(self):
        super(SystemFan, self)._onInitialize()
        pass

    def __openFan(self, Fan):
        if self.CurrentFan == Fan:
            return False
        if self.disableOpen is True:
            #            print "Disable state"
            self.calledFan = Fan
            return False

        Fan.getEntity().skipActions()
        #        self.__canceltask(False)
        if self.CurrentFan is None:
            #            print "self.CurrentFan is None"
            self.CurrentFan = Fan
            self.disableOpen = False
            #            Fan.setParam("Open",True)
            FanEntity = Fan.getEntity()
            FanEntity.openFan()

            return False
            pass

        if Fan is not self.CurrentFan and not None:
            #            print "Fan is not self.CurrentFan"
            nextFanEntity = self.CurrentFan.getEntity()
            self.disableOpen = True
            self.calledFan = Fan
            nextFanEntity.closeFan()
            return False
            pass
        return False
        pass

    def __closeFan(self, Fan):
        self.disableOpen = True
        FanEntity = Fan.getEntity()
        FanEntity.closeFan()
        pass
        return False

    def _removeCurrentFan(self, flag=False):
        #        print "Seems Fan Close"
        self.disableOpen = False
        if flag and self.CurrentFan:
            #            print "******************************"
            # Need for misfit with cancel Task, in common case flag is always False
            CurFanEntity = self.CurrentFan.getEntity()
            CurFanEntity.skipActions()
        #            if TaskManager.existTaskChain("OpenFan") is True:
        #                TaskManager.cancelTaskChain("OpenFan")
        #            pass
        #            self.__closeFan(self.CurrentFan)
        #            if TaskManager.existTaskChain("CloseFan") is True:
        #                TaskManager.cancelTaskChain("CloseFan")
        #                pass

        #        self.CurrentFan = None
        self.__turnFanForOpen()

        return False
        pass

    def __turnFanForOpen(self):
        if self.calledFan is not None:
            #            if TaskManager.existTaskChain("CloseFan") is True:
            #                TaskManager.cancelTaskChain("CloseFan")
            #                pass
            CurFanEntity = self.CurrentFan.getEntity()
            CurFanEntity.skipActions()
            self.CurrentFan = None

            self.__openFan(self.calledFan)
            self.calledFan = None
            return False
            pass
        self.CurrentFan = None
        pass
        return True
