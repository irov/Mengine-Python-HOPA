from HOPA.ConnectorsManager import ConnectorsManager

from ConnectorsConnection import ConnectorsConnection
from ConnectorsElement import ConnectorsElement


Enigma = Mengine.importEntity("Enigma")


class Connectors(Enigma):
    def __init__(self):
        super(Connectors, self).__init__()
        self.elements = {}
        self.connections = {}
        pass

    def finalize(self):
        for connectionId, connection in self.connections.items():
            connection.finalize()
            pass

        self.elements = {}
        self.connections = {}
        pass

    def _autoWin(self):
        self.finalize()
        self.enigmaComplete()
        pass

    def _stopEnigma(self):
        self.finalize()
        pass

    def _skipEnigma(self):
        self._autoWin()
        pass

    def _checkComplete(self):
        for elementId, element in self.elements.items():
            if element.isHappy() is False:
                return
                pass

        self.finalize()
        self.enigmaComplete()
        pass

    def _onActivate(self):
        GameData = ConnectorsManager.getGame(self.EnigmaName)
        for elementId, elementData in GameData.elements.items():
            stateObjectName = elementData["ObjectName"]
            needCount = elementData["NeedCount"]
            stateObject = self.object.getObject(stateObjectName)
            self.elements[elementId] = ConnectorsElement(needCount, stateObject)
            pass

        for connectionId, connectionData in GameData.connections.items():
            socketObjectName = connectionData.socketObjectName
            statesObjectName = connectionData.statesObjectName
            statesObject = self.object.getObject(statesObjectName)
            socketObject = self.object.getObject(socketObjectName)

            connection = ConnectorsConnection(socketObject, statesObject)

            for elementId in connectionData.elements:
                element = self.elements[elementId]
                connection.addElement(element)
                pass

            self.connections[connectionId] = connection
            pass
        pass

    def _playEnigma(self):
        for connectionId, connection in self.connections.items():
            connection.initialize(self._checkComplete)
            pass
        pass

    pass
