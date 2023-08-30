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

    def getRingSlot(self):
        content = self.object.getObject("Movie2_Content")
        slot = content.getMovieSlot("ring")
        return slot

    def getRing(self):
        return self.ring

    def _updateElement(self, element):
        if self.ring is None:
            return

        current_ui_element = self.ring.magic.getElement()
        if current_ui_element == element:
            return

        if current_ui_element is not None:
            self.ring.magic.removeElement()
        self.ring.magic.setElement(element)
