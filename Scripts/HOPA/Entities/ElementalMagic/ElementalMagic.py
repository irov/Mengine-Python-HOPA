from Foundation.Entity.BaseEntity import BaseEntity
from HOPA.Entities.ElementalMagic.Ring import Ring


class ElementalMagic(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "Element", Update=ElementalMagic._updateElement)

    def __init__(self):
        super(ElementalMagic, self).__init__()
        self.ring = Ring()
        self._observers = []

    def _onPreparation(self):
        self.ring.onInitialize(self, current_element=self.Element)

    def _onActivate(self):
        self.ring.onActivate()

    def _onDeactivate(self):
        self.ring.onFinalize()

    def _updateElement(self, element):
        if self.ring is None:
            return

        current_ui_element = self.ring.element.getElement()

        if current_ui_element == element:
            return

        if current_ui_element is not None:
            self.ring.element.removeElement()
        self.ring.element.setElement(element)
