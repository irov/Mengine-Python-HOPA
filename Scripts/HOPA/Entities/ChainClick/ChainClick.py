from HOPA.ChainClickManager import ChainClickManager

from ChainClickElement import ChainClickElement


Enigma = Mengine.importEntity("Enigma")


class ChainClick(Enigma):
    def __init__(self):
        super(ChainClick, self).__init__()
        self.chains = {}
        self.chainsToWin = []
        self.elements = {}
        self.currentChain = None
        pass

    def finalize(self):
        for elementId, element in self.elements.items():
            element.finalize()
            pass

        self.chains = {}
        self.chainsToWin = []
        self.elements = {}
        self.currentChain = None
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
        if len(self.chainsToWin) != 0:
            return
            pass

        self.finalize()
        self.enigmaComplete()
        return False
        pass

    def _onClickElement(self, element):
        chainId = element.getChain()

        if chainId not in self.chains:
            return
            pass

        active = element.getActive()
        if active is True:
            element.setActive(False)
            return
            pass

        element.setActive(True)

        self.clearOldChain(chainId)
        self.currentChain = chainId

        if chainId not in self.chainsToWin:
            return
            pass

        if self.checkChainComplete(chainId) is False:
            return
            pass

        self.currentChain = None
        self._checkComplete()
        pass

    def clearOldChain(self, chainId):
        if self.currentChain is None:
            return
            pass

        if self.currentChain == chainId:
            return
            pass

        oldChain = self.chains[self.currentChain]
        for elementId in oldChain.elements:
            element = self.elements[elementId]
            element.setActive(False)
            pass
        pass

    def checkChainComplete(self, chainId):
        chain = self.chains[chainId]
        for elementId in chain.elements:
            element = self.elements[elementId]
            if element.getActive() is False:
                return False
                pass

        for elementId in chain.elements:
            element = self.elements[elementId]
            element.complete()
            del self.elements[elementId]
            pass
        self.chainsToWin.remove(chainId)
        del self.chains[chainId]
        pass

    def _onActivate(self):
        GameData = ChainClickManager.getGame(self.EnigmaName)
        for elementId, elementData in GameData.elements.items():
            itemObject = self.object.getObject(elementData["ObjectName"])
            itemClickedObject = self.object.getObject(elementData["ClickedObjectName"])

            movieCompleteObject = self.object.generateObject(elementData["CompleteObjectName"],
                                                             elementData["CompleteObjectName"])

            element = ChainClickElement(itemObject, itemClickedObject, movieCompleteObject)
            self.elements[elementId] = element
            pass

        for chainId, chain in GameData.chains.items():
            self.chains[chainId] = chain
            if chain.needToWin == 1:
                self.chainsToWin.append(chainId)

            for elementId in chain.elements:
                element = self.elements[elementId]
                element.setChain(chainId)

    def _playEnigma(self):
        for elementId, element in self.elements.items():
            element.initialize(self._onClickElement)
