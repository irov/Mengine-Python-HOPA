from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.ElementalMagicManager import ElementalMagicManager
from HOPA.TipManager import TipManager


class MacroElementalMagicUse(MacroCommand):

    def _onValues(self, values):
        self.socket_name = values[0]
        self.magic_id = values[1]
        self.tip_id = values[2]

        self.socket_obj = None

    def _onInitialize(self):
        if _DEVELOPMENT is True:
            # check socket
            if self.hasObject(self.socket_name) is False:
                self.initializeFailed("{!r} not found object {!r} in group {!r}".format(
                    self.CommandType, self.socket_name, self.GroupName))

            # check magic
            magic_params = ElementalMagicManager.getMagicParams(self.magic_id)
            if magic_params is None:
                self.initializeFailed("Magic with id {!r} not found".format(self.magic_id))

            # check tip
            if TipManager.hasTip(self.tip_id) is False:
                self.initializeFailed("Tip {!r} not found".format(self.tip_id))

        _, self.socket_obj = self.findObject(self.socket_name)

    def _onGenerate(self, source):
        magic_params = ElementalMagicManager.getMagicParams(self.magic_id)

        Quest = self.addQuest(source, "ElementalMagicUse", SceneName=self.SceneName, GroupName=self.GroupName,
                              Object=self.socket_obj, MagicId=self.magic_id, Element=magic_params.element)

        with Quest as tc_quest:
            tc_quest.addNotify(Notificator.onTipActivateWithoutParagraphs, self.socket_obj, self.tip_id)
            tc_quest.addTask("TaskSocketUseElementalMagic", Object=self.socket_obj, SocketName=self.socket_name,
                             Element=magic_params.element, TipName=self.tip_id)
            tc_quest.addNotify(Notificator.onTipRemoveWithoutParagraphs, self.tip_id)
