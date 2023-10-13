from Foundation.System import System
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.Entities.ElementalMagic.Ring import InvalidClick
from HOPA.TipManager import TipManager
from HOPA.System.SystemTooltips import ALIAS_ENV, ALIAS_CURSOR_TEXT, ID_EMPTY_TEXT


class SystemElementalMagic(System):

    def _onParams(self, params):
        pass

    def _onRun(self):
        self.addObserver(Notificator.onZoomEnter, self._cbUpdateReadyState)
        self.addObserver(Notificator.onZoomLeave, self._cbUpdateReadyState)

        if ElementalMagicManager.getConfig("EnableTooltips", True) is True:
            self.addObserver(Notificator.onElementalMagicRingMouseEnter, self._cbRingMouseEnter)
            self.addObserver(Notificator.onElementalMagicRingMouseLeave, self._cbRingMouseLeave)

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

    def _cbMagicReady(self):
        if ElementalMagicManager.getConfig("SoundEffectOnReady", False) is True:
            pass  # todo: play sound effect
        return False

    def _cbMagicUse(self, element):
        if ElementalMagicManager.getConfig("SoundEffectOnUse", False) is True:
            pass  # todo: play sound effect
        ElementalMagicManager.setPlayerElement(None)
        return False

    def _cbMagicPick(self, element):
        if ElementalMagicManager.getConfig("SoundEffectOnPick", False) is True:
            pass  # todo: play sound effect

        if ElementalMagicManager.isElementExists(element) is False:
            Trace.log("System", 0, "Can't pick element {} because it doesn't exist".format(element))
            return False
        ElementalMagicManager.setPlayerElement(element)

        return False

    def _cbMagicInvalidClick(self, status):
        if ElementalMagicManager.getConfig("SoundEffectOnInvalidClick", False) is True:
            pass  # todo: play sound effect

        if status == InvalidClick.Miss:
            pass  # todo: show mind
        elif status == InvalidClick.WrongElement:
            tip_id = ElementalMagicManager.getConfig("TipInvalidClickWrongElement", "ID_Tip_Magic_WrongElement")
            TipManager.showTip(tip_id)
        elif status == InvalidClick.EmptyRing:
            tip_id = ElementalMagicManager.getConfig("TipInvalidClickEmptyRing", "ID_Tip_Magic_EmptyRing")
            TipManager.showTip(tip_id)
        return False

    # tooltips

    def _setTooltip(self, text_id):
        if text_id is None:
            return

        Mengine.removeTextAliasArguments(ALIAS_ENV, ALIAS_CURSOR_TEXT)
        Mengine.setTextAlias(ALIAS_ENV, ALIAS_CURSOR_TEXT, text_id)

    def _removeTooltip(self):
        Mengine.removeTextAliasArguments(ALIAS_ENV, ALIAS_CURSOR_TEXT)
        Mengine.setTextAlias(ALIAS_ENV, ALIAS_CURSOR_TEXT, ID_EMPTY_TEXT)

    def _cbRingMouseEnter(self, ring):
        current_magic_element = ring.magic.getElement()

        if current_magic_element is not None:
            elemental_data = ElementalMagicManager.getElementParams(current_magic_element)
            text_id = elemental_data.tooltip_text_id
        else:
            text_id = ElementalMagicManager.getConfig("DefaultTooltip", "ID_TooltipElementalMagicRing")

        self._setTooltip(text_id)
        return False

    def _cbRingMouseLeave(self, ring):
        self._removeTooltip()
        return False

    # serialization

    def _onSave(self):
        save = {
            "player_element": ElementalMagicManager.getPlayerElement()
        }
        return save

    def _onLoad(self, save):
        ElementalMagicManager.setPlayerElement(save.get("player_element"))
