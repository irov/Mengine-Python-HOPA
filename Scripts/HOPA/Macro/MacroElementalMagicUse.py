from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.ElementalMagicManager import ElementalMagicManager, QUEST_USE_MAGIC_NAME
from HOPA.TipManager import TipManager


class MacroElementalMagicUse(MacroCommand):

    def _onValues(self, values):
        self.SocketName = values[0]
        self.MagicId = values[1]
        self.TipName = values[2]

        self.Element = None
        self.SocketObject = None

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            # check socket
            if self.hasObject(self.SocketName) is False:
                self.initializeFailed("{!r} not found object {!r} in group {!r}".format(
                    self.CommandType, self.SocketName, self.GroupName))

            # check magic
            magic_params = ElementalMagicManager.getMagicParams(self.MagicId)
            if magic_params is None:
                self.initializeFailed("Magic with id {!r} not found".format(self.MagicId))

            # check tip
            if TipManager.hasTip(self.TipName) is False:
                self.initializeFailed("Tip {!r} not found".format(self.TipName))

        _, self.SocketObject = self.findObject(self.SocketName)

        magic_params = ElementalMagicManager.getMagicParams(self.MagicId)
        self.Element = magic_params.element

    def _tryNotifyReady(self, source):
        if ElementalMagicManager.getPlayerElement() == self.Element:
            source.addNotify(Notificator.onElementalMagicReady)

    def _onGenerate(self, source):
        Quest = self.addQuest(source, QUEST_USE_MAGIC_NAME, SceneName=self.SceneName, GroupName=self.GroupName,
                              Object=self.SocketObject, MagicId=self.MagicId, Element=self.Element)

        with Quest as tc_quest:
            tc_quest.addScope(self._tryNotifyReady)
            tc_quest.addNotify(Notificator.onTipActivateWithoutParagraphs, self.SocketObject, self.TipName)
            tc_quest.addTask("TaskSocketUseElementalMagic", Object=self.SocketObject, SocketName=self.SocketName,
                             Element=self.Element)
            tc_quest.addNotify(Notificator.onTipRemoveWithoutParagraphs, self.TipName)
