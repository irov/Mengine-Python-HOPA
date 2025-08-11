from HOPA.ColumnChainManager import ColumnChainManager

from Column import Column

Enigma = Mengine.importEntity("Enigma")

class ColumnChain(Enigma):
    def __init__(self):
        super(ColumnChain, self).__init__()
        self.GameData = {}
        self.columnBySocket = {}
        self.socketClickObserver = None
        self.columnPlacedObserver = None
        pass

    def _stopEnigma(self):
        super(ColumnChain, self)._stopEnigma()
        if self.socketClickObserver is not None:
            Notification.removeObserver(self.socketClickObserver)
            self.socketClickObserver = None
            pass

        if self.columnPlacedObserver is not None:
            Notification.removeObserver(self.columnPlacedObserver)
            self.columnPlacedObserver = None
            pass
        pass

    def _playEnigma(self):
        self.GameData = ColumnChainManager.getColumnChain(self.EnigmaName)
        dataPack = self.GameData.getColumnBySocket()

        for key, value in dataPack.iteritems():
            socket = self.object.getObject(key)
            socket.setEnable(True)
            socket.setInteractive(True)
            column = Column(value, self.object)
            self.columnBySocket[socket] = column
            pass

        self.socketClickObserver = Notification.addObserver(Notificator.onSocketClick, self._onColumnSocketClick)
        self.columnPlacedObserver = Notification.addObserver(Notificator.onColumnPlaced, self._onColumnPlaced)
        pass

    def _onColumnSocketClick(self, curSocket):
        if curSocket not in self.columnBySocket.keys():
            return False
            pass
        curColumn = self.columnBySocket[curSocket]
        curColumn.columnUpdate(curSocket)
        return False
        pass

    def _onColumnPlaced(self):
        for column in self.columnBySocket.values():
            if column.isWinState():
                continue
                pass
            return False
            pass
        self.setComplete()
        return False
