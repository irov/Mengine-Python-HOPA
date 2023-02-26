from Foundation.Entity.BaseEntity import BaseEntity
from Notification import Notification

from ExtrasConceptManager import ExtrasConceptManager

class ExtrasConcept(BaseEntity):
    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)
        pass

    def _updateConcept(self, value):
        if value is None:
            pass
        pass

    def __init__(self):
        super(ExtrasConcept, self).__init__()
        self.ButtonLeft = None
        self.ButtonRight = None
        self.ButtonClickObserver = None
        self.concepts = []
        self.currentIndex = 0
        pass

    def _onPreparation(self):
        super(ExtrasConcept, self)._onPreparation()
        Data = ExtrasConceptManager.getData()

        for spriteName in Data:
            sprite = self.object.getObject(spriteName)
            sprite.setEnable(False)

            self.concepts.append(sprite)
            pass

        self.ButtonLeft = self.object.getObject("Button_Left")
        self.ButtonLeft.setInteractive(True)

        self.ButtonRight = self.object.getObject("Button_Right")
        self.ButtonRight.setInteractive(True)
        self.concepts[self.currentIndex].setEnable(True)
        pass

    def __update(self, value):
        self.concepts[self.currentIndex].setEnable(False)

        tmpValue = self.currentIndex + value
        if tmpValue >= len(self.concepts):
            tmpValue = 0
            pass
        elif tmpValue < 0:
            tmpValue = len(self.concepts) - 1
            pass

        self.currentIndex = tmpValue
        self.concepts[self.currentIndex].setEnable(True)
        pass

    def _onActivate(self):
        super(ExtrasConcept, self)._onActivate()
        self.ButtonClickObserver = Notification.addObserver(Notificator.onButtonClick, self.__onButtonClick)
        pass

    def __onButtonClick(self, button):
        if button is self.ButtonRight:
            self.__update(1)
            return False
            pass
        if button is self.ButtonLeft:
            self.__update(-1)
            return False
            pass

        return False
        pass

    def _onDeactivate(self):
        super(ExtrasConcept, self)._onDeactivate()

        Notification.removeObserver(self.ButtonClickObserver)
        self.ButtonClickObserver = None

        self.ButtonLeft.setInteractive(False)
        self.ButtonRight.setInteractive(False)
        pass

    pass