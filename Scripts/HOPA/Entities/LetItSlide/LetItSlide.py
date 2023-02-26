from Notification import Notification

from Field import Field
from LetItSlideElement import LetItSlideElement
from LetItSlideManager import LetItSlideManager

Enigma = Mengine.importEntity("Enigma")

class LetItSlide(Enigma):
    def __init__(self):
        super(LetItSlide, self).__init__()
        self.gameData = {}
        self.field = None
        self.items = {}
        self.winCombination = {}
        pass

    def _onPreparation(self):
        super(LetItSlide, self)._onPreparation()
        self.gameData = LetItSlideManager.getGameData(self.EnigmaName)
        self.field = Field(self.gameData)
        self.items = {}
        self.winCombination = self.gameData.getWinCombination()
        pass

    def setupItems(self):
        itemsData = self.gameData.getItemData()

        for id, itemData in itemsData.iteritems():
            position = itemData.getPosition()
            movieObject = itemData.getMovieObject()
            isHorizontal = itemData.getHorizontal()

            movieEntity = movieObject.getEntity()
            socket = movieEntity.getSocket(str(id))
            length = itemData.getLength()

            item = LetItSlideElement(id, movieObject, isHorizontal, socket, length, self.field)
            item.setPosition(position)
            item.onActivate()
            self.items[id] = item
            pass
        pass

    def _onActivate(self):
        pass

    def playEnigma(self):
        self.onCheckWin = Notification.addObserver(Notificator.onLetItSlideWin, self.__onCheckWin)

        startPosition = self.getStartPosition()
        self.field.setupField(startPosition)
        self.setupItems()
        pass

    def __onCheckWin(self, itemID, position):
        if itemID in self.winCombination.iterkeys():
            if self.winCombination[itemID] == position:
                self.enigmaComplete()
                # self.Destroy()
                return True
                pass
            pass
        return False
        pass

    def getStartPosition(self):
        movieStart = self.object.getObject("Movie_Start")
        movieStartEntity = movieStart.getEntity()
        slotStart = movieStartEntity.getMovieSlot("start")
        startPosX = slotStart.getWorldPosition()[0]
        startPosY = slotStart.getWorldPosition()[1]
        startPos = (startPosX, startPosY)
        return startPos
        pass

    def _stopEnigma(self):
        super(LetItSlide, self)._stopEnigma()
        return False
        pass

    def onDeactivate(self):
        super(LetItSlide, self).onDeactivate()
        Notification.removeObserver(self.onCheckWin)
        self.Destroy()
        pass

    def Destroy(self):
        self.field.Destroy()

        for item in self.items.values():
            item.Destroy()
            pass

        self.gameData = {}
        self.field = None
        self.items = {}
        self.winCombination = {}
        pass