from Foundation.Entity.BaseEntity import BaseEntity
from Notification import Notification

from ExtrasEnigmaManager import ExtrasEnigmaManager


class ExtrasEnigma(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def __init__(self):
        super(ExtrasEnigma, self).__init__()
        self.buttonPlay = None
        self.buttonLeft = None
        self.buttonRight = None
        self.currentIndex = 0
        self.Collection = {}
        self.sprites = []
        self.ButtonClickObserver = None
        pass

    def _onPreparation(self):
        super(ExtrasEnigma, self)._onPreparation()

        Data = ExtrasEnigmaManager.getData(self.object.getName())

        self.buttonPlay = self.object.getObject("Button_Play")
        self.buttonLeft = self.object.getObject("Button_Left")
        self.buttonRight = self.object.getObject("Button_Right")

        self.buttonLeft.setInteractive(True)
        self.buttonPlay.setInteractive(True)
        self.buttonRight.setInteractive(True)

        for spriteName, dataTuple in Data.iteritems():
            sprite = self.object.getObject(spriteName)
            sprite.setEnable(False)

            self.sprites.append(sprite)
            self.Collection[sprite] = dataTuple
            pass

        self.sprites[self.currentIndex].setEnable(True)
        pass

    def _onActivate(self):
        self.ButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)

        pass

    def __onButtonClick(self, button):
        if button is self.buttonRight:
            self.__updateSprite(1)
            return False
            pass
        if button is self.buttonLeft:
            self.__updateSprite(-1)
            return False
            pass
        if button is self.buttonPlay:
            self.__activateEnigma()
            return False
            pass
        return False
        pass

    def __updateSprite(self, value):
        self.sprites[self.currentIndex].setEnable(False)

        tmpValue = self.currentIndex + value
        if tmpValue >= len(self.sprites):
            tmpValue = 0
            pass
        elif tmpValue < 0:
            tmpValue = len(self.sprites) - 1
            pass

        self.currentIndex = tmpValue
        self.sprites[self.currentIndex].setEnable(True)
        pass

    def __activateEnigma(self):
        enigmaName, sceneName = self.Collection[self.sprites[self.currentIndex]]

        Notification.notify(Notificator.onExtraEnigmaPlay, enigmaName, sceneName)
        pass

    def _onDeactivate(self):
        Notification.removeObserver(self.ButtonClickObserver)
        self.ButtonClickObserver = None

        self.buttonLeft.setInteractive(False)
        self.buttonRight.setInteractive(False)
        self.buttonPlay.setInteractive(False)

        pass
