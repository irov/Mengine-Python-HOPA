from Foundation.DemonManager import DemonManager
from Foundation.System import System

class SystemMagicGlove(System):
    def _onRun(self):
        self.addObserver(Notificator.onRuneReady, self.__cbReaction)
        self.addObserver(Notificator.onRuneListChanges, self.__cbReaction)
        self.addObserver(Notificator.onSceneChange, self.__cbReaction)
        self.addObserver(Notificator.onZoomEnter, self.__cbReaction)
        self.addObserver(Notificator.onZoomLeave, self.__cbReaction)
        return True

    def __cbReaction(self, *_, **__):
        demon_magic_glove = DemonManager.getDemon('MagicGlove')
        active_use_rune_quest = demon_magic_glove.getActiveUseRuneQuest()
        runes = demon_magic_glove.getParam("Runes")

        if len(demon_magic_glove.getParam("Runes")) == 0:
            demon_magic_glove.setParam("State", "Idle")
            return False

        if active_use_rune_quest:
            if active_use_rune_quest.params['Rune_ID'] in runes:
                demon_magic_glove.setParam("State", "Light")
                return False

        demon_magic_glove.setParam("State", "Ready")
        return False