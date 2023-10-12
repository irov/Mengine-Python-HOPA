from Foundation.Entity.BaseEntity import BaseEntity
from HOPA.Entities.ElementalMagic.Ring import Ring


class ElementalMagic(BaseEntity):

    @staticmethod
    def declareORM(Type):
        BaseEntity.declareORM(Type)

        Type.addActionActivate(Type, "Element", Update=ElementalMagic._updateElement)

    def __init__(self):
        super(ElementalMagic, self).__init__()
        self.ring = None
        self._observers = []

    def _onPreparation(self):
        self._observers = [
            Notification.addObserver(Notificator.onElementalMagicReady, self._cbMagicReady),
            Notification.addObserver(Notificator.onElementalMagicReadyEnd, self._cbMagicReadyEnd),
        ]

        self.ring = Ring()
        self.ring.onInitialize(self, current_element=self.Element)

    def _onActivate(self):
        self.ring.onActivate()

    def _onDeactivate(self):
        for observer in self._observers:
            Notification.removeObserver(observer)
        self._observers = []

        self.ring.onFinalize()
        self.ring = None

    def _cbMagicReady(self):
        self.ring.setReady(True)
        return False

    def _cbMagicReadyEnd(self):
        self.ring.setReady(False)
        return False

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
            if element is None:
                # remove element after deactivate or play Release
                self.ring.magic.releaseElement()
                return

            # remove element immediately
            self.ring.magic.removeElement()

        if element is not None:
            self.ring.magic.setElement(element)
