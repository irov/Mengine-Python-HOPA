from Foundation.System import System
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.Entities.ElementalMagic.Ring import InvalidClick


class SystemElementalMagic(System):

    def _onParams(self, params):
        pass

    def _onRun(self):
        self.addObserver(Notificator.onZoomEnter, self._cbUpdateReadyState)
        self.addObserver(Notificator.onZoomLeave, self._cbUpdateReadyState)

        self.addObserver(Notificator.onElementalMagicReady, self._cbMagicReady)
        self.addObserver(Notificator.onElementalMagicUse, self._cbMagicUse)
        self.addObserver(Notificator.onElementalMagicPick, self._cbMagicPick)
        self.addObserver(Notificator.onElementalMagicInvalidClick, self._cbMagicInvalidClick)
        return True

    def _onStop(self):
        return True

    # observers

    def _cbUpdateReadyState(self, *_, **__):
        if ElementalMagicManager.isMagicReady() is True:
            Notification.notify(Notificator.onElementalMagicReady)
        else:
            Notification.notify(Notificator.onElementalMagicReadyEnd)
        return False

    def _cbMagicReady(self, element):
        return False

    def _cbMagicUse(self, element):
        # todo: play sound effect
        return False

    def _cbMagicPick(self, element):
        # todo: play sound effect
        return False

    def _cbMagicInvalidClick(self, status):
        # todo: play sound effect
        if status == InvalidClick.Miss:
            pass # todo: show mind
        elif status == InvalidClick.WrongElement:
            pass # todo: show mind
        elif status == InvalidClick.EmptyRing:
            pass # todo: show mind
        return False

    # serialization

    def _onSave(self):
        save = {
            "player_element": ElementalMagicManager.getPlayerElement()
        }
        return save

    def _onLoad(self, save):
        ElementalMagicManager.setPlayerElement(save.get("player_element"))
