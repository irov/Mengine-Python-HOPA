from HOPA.Macro.MacroCommand import MacroCommand
from HOPA.ElementalMagicManager import ElementalMagicManager, QUEST_PICK_ELEMENT_NAME
from HOPA.TipManager import TipManager


class MacroElementalMagicPick(MacroCommand):
    def _onValues(self, values):
        self.SocketName = values[0]
        self.MagicId = values[1]
        self.TipName = values[2]     # "can't get element now"

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

    def _onGenerate(self, source):
        magic_params = ElementalMagicManager.getMagicParams(self.MagicId)

        isRepeat = self.isRepeatScenario()

        if isRepeat is False:
            Quest = self.addQuest(source, QUEST_PICK_ELEMENT_NAME, SceneName=self.SceneName, GroupName=self.GroupName,
                                  Object=self.SocketObject, MagicId=self.MagicId, Element=magic_params.element)

            with Quest as tc_quest:
                tc_quest.addTask("TaskSocketPickElementalMagic", SocketName=self.SocketName,
                                 Element=magic_params.element, TipName=self.TipName)

        else:

            source.addTask("TaskSocketPickElementalMagic", SocketName=self.SocketName,
                           Element=magic_params.element, TipName=self.TipName)



